# SWIFT / ISO 20022 Integration Patterns

**Type**: Domain Pattern  
**Applicability**: Banking — payments, settlements, account reporting

---

## ISO 20022 Message Families

| Message type | XML namespace | Usage |
|---|---|---|
| `pacs.008` | `urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10` | Credit transfer (SWIFT gpi, SEPA CT) |
| `pacs.002` | `urn:iso:std:iso:20022:tech:xsd:pacs.002.001.12` | Payment status report |
| `pacs.004` | `urn:iso:std:iso:20022:tech:xsd:pacs.004.001.11` | Return of funds |
| `camt.053` | `urn:iso:std:iso:20022:tech:xsd:camt.053.001.10` | Bank-to-customer statement |
| `camt.054` | `urn:iso:std:iso:20022:tech:xsd:camt.054.001.10` | Debit/credit notification |
| `pain.001` | `urn:iso:std:iso:20022:tech:xsd:pain.001.001.11` | Customer credit transfer initiation |

---

## Spring Integration Pattern for SWIFT/ISO 20022

```java
// Domain model — always use domain types, not raw XML fields
public record PaymentInstruction(
    String endToEndId,           // ISO 20022 EndToEndId — immutable reference
    String transactionId,        // UETR for SWIFT gpi (UUID)
    MonetaryAmount amount,       // always BigDecimal + Currency
    BicIdentifier creditorBic,
    IbanAccountNumber creditorIban,
    BicIdentifier debtorBic,
    IbanAccountNumber debtorIban,
    LocalDate settlementDate,
    PaymentPriority priority
) {}

// Value objects — never raw strings for identifiers
public record BicIdentifier(String value) {
    public BicIdentifier {
        if (!value.matches("^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$"))
            throw new InvalidBicException(value);
    }
}

public record IbanAccountNumber(String value) {
    public IbanAccountNumber {
        if (!IbanValidator.isValid(value))
            throw new InvalidIbanException(value);
    }
}
```

### XML Unmarshalling (pacs.008)

```java
@Component
public class Pacs008MessageParser {

    private final JAXBContext jaxbContext;

    public Pacs008MessageParser() throws JAXBException {
        this.jaxbContext = JAXBContext.newInstance(Document.class);  // ISO 20022 generated class
    }

    public List<PaymentInstruction> parse(String xmlPayload) {
        try {
            var unmarshaller = jaxbContext.createUnmarshaller();
            var document = (Document) unmarshaller.unmarshal(new StringReader(xmlPayload));
            return document.getFIToFICstmrCdtTrf()
                .getCdtTrfTxInf()
                .stream()
                .map(this::toDomain)
                .toList();
        } catch (JAXBException e) {
            throw new MessageParseException("Failed to parse pacs.008", e);
        }
    }

    private PaymentInstruction toDomain(CreditTransferTransaction62 tx) {
        return new PaymentInstruction(
            tx.getPmtId().getEndToEndId(),
            tx.getPmtId().getUETR(),
            new MonetaryAmount(tx.getIntrBkSttlmAmt().getValue(), Currency.getInstance(tx.getIntrBkSttlmAmt().getCcy())),
            new BicIdentifier(tx.getCdtrAgt().getFinInstnId().getBICFI()),
            new IbanAccountNumber(tx.getCdtrAcct().getId().getIBAN()),
            new BicIdentifier(tx.getDbtrAgt().getFinInstnId().getBICFI()),
            new IbanAccountNumber(tx.getDbtrAcct().getId().getIBAN()),
            tx.getIntrBkSttlmDt().toGregorianCalendar().toZonedDateTime().toLocalDate(),
            PaymentPriority.from(tx.getSttlmTmIndctn())
        );
    }
}
```

---

## SEPA Credit Transfer Validation Rules

```java
@Component
public class SepaCreditTransferValidator {

    public ValidationResult validate(PaymentInstruction payment) {
        var errors = new ArrayList<String>();

        // SEPA amount limits
        if (payment.amount().value().compareTo(BigDecimal.valueOf(999_999_999.99)) > 0)
            errors.add("SEPA CT amount exceeds €999,999,999.99 limit");

        // SEPA only EUR
        if (!payment.amount().currency().getCurrencyCode().equals("EUR"))
            errors.add("SEPA CT requires EUR currency; got: " + payment.amount().currency());

        // Same-day settlement: must be submitted before cut-off
        if (payment.priority() == PaymentPriority.URGENT && LocalTime.now().isAfter(SEPA_CUTOFF))
            errors.add("Urgent SEPA CT submitted after cut-off time " + SEPA_CUTOFF);

        // IBAN country code must be SEPA-eligible
        var creditorCountry = payment.creditorIban().value().substring(0, 2);
        if (!SEPA_COUNTRIES.contains(creditorCountry))
            errors.add("Creditor IBAN country " + creditorCountry + " is not in SEPA zone");

        return errors.isEmpty() ? ValidationResult.valid() : ValidationResult.invalid(errors);
    }

    private static final LocalTime SEPA_CUTOFF = LocalTime.of(16, 0);
    private static final Set<String> SEPA_COUNTRIES = Set.of(
        "AT","BE","BG","CH","CY","CZ","DE","DK","EE","ES","FI","FR","GB",
        "GR","HR","HU","IE","IS","IT","LI","LT","LU","LV","MT","NL","NO",
        "PL","PT","RO","SE","SI","SK"
    );
}
```

---

## SWIFT gpi Tracking

SWIFT gpi requires updating `UETR` status at each processing stage:

```java
public enum GpiStatus {
    ACCC,   // AcceptedSettlementCompleted
    ACSP,   // AcceptedSettlementInProcess
    RJCT,   // Rejected
    PDNG    // Pending
}

@Service
public class GpiTrackingService {
    public void updateStatus(String uetr, GpiStatus status, String reasonCode) {
        // Publish pacs.002 back to SWIFT gpi tracker
        var statusReport = buildPacs002(uetr, status, reasonCode);
        swiftConnector.send(statusReport);

        // Update internal tracking DB
        paymentRepository.updateGpiStatus(uetr, status, Instant.now());
        log.info("gpi_status_updated", uetr=uetr, status=status.name());
    }
}
```

---

## Compliance Hooks

Every payment must pass through:

```
1. Sanctions screening        → OFAC, EU, UN sanctions lists
2. AML transaction monitoring → velocity checks, amount thresholds
3. Fraud detection            → real-time scoring
4. Correspondent bank limits  → bilateral credit limits
```

```java
@Service
public class PaymentComplianceGateway {

    public ComplianceResult screen(PaymentInstruction payment) {
        var sanctions  = sanctionsService.screen(payment.creditorIban(), payment.creditorBic());
        var aml        = amlService.assess(payment);
        var fraud      = fraudService.score(payment);

        if (sanctions.isHit() || aml.isHighRisk()) {
            auditLogger.logComplianceHold(payment, sanctions, aml);
            return ComplianceResult.hold("COMPLIANCE_REVIEW_REQUIRED");
        }
        return ComplianceResult.pass();
    }
}
```

---

## Key Rules

- **Never store raw BIC/IBAN as unvalidated strings** — always use value objects
- **BigDecimal for all monetary amounts** — never float/double
- **Idempotent processing** — check EndToEndId before processing; SWIFT can redeliver
- **Audit log every state transition** — regulators can request 7-year payment history
- **Encrypt PII in transit and at rest** — account numbers, beneficiary names
