# HL7 FHIR R4 Integration Patterns

**Type**: Domain Pattern  
**Applicability**: Healthcare — clinical data exchange, EHR integration, patient records

---

## FHIR Resources Quick Reference

| Resource | Use case |
|---|---|
| `Patient` | Demographics, identifiers (NHS number, PAS number) |
| `Encounter` | Clinical visit, admission, discharge |
| `Observation` | Vital signs, lab results, measurements |
| `Condition` | Diagnosis, problem list |
| `MedicationRequest` | Prescriptions |
| `DiagnosticReport` | Lab/radiology reports with results |
| `Procedure` | Surgical and clinical procedures |
| `AllergyIntolerance` | Drug and food allergies |
| `Appointment` | Scheduling |
| `Bundle` | Collection of resources (transaction, message, document) |

---

## FHIR Resource Model (Java with HAPI FHIR)

```xml
<!-- pom.xml -->
<dependency>
    <groupId>ca.uhn.hapi.fhir</groupId>
    <artifactId>hapi-fhir-structures-r4</artifactId>
    <version>7.0.0</version>
</dependency>
<dependency>
    <groupId>ca.uhn.hapi.fhir</groupId>
    <artifactId>hapi-fhir-client</artifactId>
    <version>7.0.0</version>
</dependency>
```

### Creating a Patient Resource

```java
@Service
public class PatientFhirMapper {

    public Patient toFhir(PatientRecord record) {
        var patient = new Patient();

        // NHS Number identifier (UK-specific)
        patient.addIdentifier()
            .setSystem("https://fhir.nhs.uk/Id/nhs-number")
            .setValue(record.nhsNumber())
            .setUse(Identifier.IdentifierUse.OFFICIAL);

        // Name
        patient.addName()
            .setFamily(record.surname())
            .addGiven(record.forename())
            .setUse(HumanName.NameUse.OFFICIAL);

        // Date of birth
        patient.setBirthDateElement(new DateType(record.dateOfBirth().toString()));

        // Gender
        patient.setGender(record.gender() == Gender.MALE
            ? Enumerations.AdministrativeGender.MALE
            : Enumerations.AdministrativeGender.FEMALE);

        // Contact
        patient.addTelecom()
            .setSystem(ContactPoint.ContactPointSystem.PHONE)
            .setValue(record.phone())
            .setUse(ContactPoint.ContactPointUse.HOME);

        return patient;
    }
}
```

### Observation (Vital Signs)

```java
public Observation buildBloodPressureObservation(String patientId, int systolic, int diastolic, Instant measured) {
    var obs = new Observation();
    obs.setStatus(Observation.ObservationStatus.FINAL);
    obs.addCategory()
        .addCoding()
        .setSystem("http://terminology.hl7.org/CodeSystem/observation-category")
        .setCode("vital-signs");

    // LOINC code for blood pressure panel
    obs.getCode().addCoding()
        .setSystem("http://loinc.org")
        .setCode("85354-9")
        .setDisplay("Blood pressure panel");

    obs.setSubject(new Reference("Patient/" + patientId));
    obs.setEffective(new DateTimeType(Date.from(measured)));

    // Systolic component
    var systolicComp = obs.addComponent();
    systolicComp.getCode().addCoding().setSystem("http://loinc.org").setCode("8480-6").setDisplay("Systolic BP");
    systolicComp.setValue(new Quantity().setValue(systolic).setUnit("mmHg")
        .setSystem("http://unitsofmeasure.org").setCode("mm[Hg]"));

    // Diastolic component
    var diastolicComp = obs.addComponent();
    diastolicComp.getCode().addCoding().setSystem("http://loinc.org").setCode("8462-4").setDisplay("Diastolic BP");
    diastolicComp.setValue(new Quantity().setValue(diastolic).setUnit("mmHg")
        .setSystem("http://unitsofmeasure.org").setCode("mm[Hg]"));

    return obs;
}
```

---

## FHIR REST API Patterns

```java
@Service
public class FhirServerClient {

    private final IGenericClient fhirClient;

    public FhirServerClient(@Value("${fhir.server.url}") String serverUrl) {
        var ctx = FhirContext.forR4();
        this.fhirClient = ctx.newRestfulGenericClient(serverUrl);
    }

    // Search patients by NHS number
    public Optional<Patient> findByNhsNumber(String nhsNumber) {
        var bundle = fhirClient.search()
            .forResource(Patient.class)
            .where(Patient.IDENTIFIER.exactly()
                .systemAndIdentifier("https://fhir.nhs.uk/Id/nhs-number", nhsNumber))
            .returnBundle(Bundle.class)
            .execute();

        return bundle.getEntry().stream()
            .map(e -> (Patient) e.getResource())
            .findFirst();
    }

    // Create or update (upsert) a patient
    public MethodOutcome upsertPatient(Patient patient) {
        return fhirClient.update()
            .resource(patient)
            .conditional()
            .where(Patient.IDENTIFIER.exactly()
                .systemAndIdentifier("https://fhir.nhs.uk/Id/nhs-number",
                    patient.getIdentifierFirstRep().getValue()))
            .execute();
    }

    // Transaction bundle — atomic multi-resource operation
    public Bundle submitTransaction(Bundle transactionBundle) {
        transactionBundle.setType(Bundle.BundleType.TRANSACTION);
        return fhirClient.transaction().withBundle(transactionBundle).execute();
    }
}
```

---

## SMART on FHIR Authentication (OAuth2)

```yaml
# application.yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://authorize.fhir.nhs.uk
```

```java
// SMART scopes check
@PreAuthorize("hasAuthority('SCOPE_patient/Patient.read')")
public Patient getPatient(String patientId) { ... }

@PreAuthorize("hasAuthority('SCOPE_patient/Observation.write')")
public Observation recordObservation(Observation obs) { ... }
```

---

## Data Protection Rules (FHIR + GDPR/DSPT)

- **Minimum necessary** — only include FHIR elements required for the use case; do not include full patient record if only demographics needed
- **Pseudonymisation** — replace NHS number with internal pseudonym for analytics pipelines
- **Audit trail** — log every FHIR resource access: who, what resource, what operation, when
- **Consent** — check patient consent flags before sharing data with third parties (`Consent` resource)
- **Data residency** — FHIR server and backups must remain within UK data centres (NHS DSP Toolkit requirement)
- **Retention** — clinical records: minimum 8 years adult, 25 years pediatric (UK); implement via FHIR `AuditEvent`

---

## SNOMED CT + LOINC Coding

Always use standard code systems:

```java
// ✅ Coded diagnosis
var condition = new Condition();
condition.getCode().addCoding()
    .setSystem("http://snomed.info/sct")
    .setCode("44054006")
    .setDisplay("Diabetes mellitus type 2");

// ✅ Coded lab result
var obs = new Observation();
obs.getCode().addCoding()
    .setSystem("http://loinc.org")
    .setCode("2339-0")
    .setDisplay("Glucose [Mass/volume] in Blood");

// ❌ Free-text diagnosis only — not queryable, not interoperable
condition.getCode().setText("Type 2 diabetes");  // alone, without coding
```
