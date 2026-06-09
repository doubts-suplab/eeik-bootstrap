# Claims Processing Patterns

**Type**: Domain Pattern  
**Applicability**: General insurance — P&C, motor, health, life claims

---

## Claim Lifecycle State Machine

```
FNOL                     First Notice of Loss — initial report
  ↓
REGISTERED               Claim created; unique claim reference assigned
  ↓
ACKNOWLEDGED             Insured notified; handler assigned
  ↓
UNDER_INVESTIGATION      Evidence gathering, third-party contact
  ↓
ASSESSMENT               Loss adjuster review; reserve set/updated
  ↓
SETTLEMENT_OFFER         Offer made to insured
  ↓
AGREED / DISPUTED        Insured accepts or disputes
  ↓
PAYMENT_AUTHORISED       Finance approval for payment
  ↓
PAID                     Payment made; recovery if applicable
  ↓
CLOSED                   Claim finalized; reserve released
  ↓
REOPENED (optional)      New information or legal action
```

---

## Domain Model

```java
public class Claim {
    private final ClaimReference reference;       // immutable, system-assigned
    private final PolicyReference policyRef;
    private final LossEvent lossEvent;
    private ClaimStatus status;
    private Reserve reserve;
    private final List<ClaimNote> notes = new ArrayList<>();
    private final List<PaymentTransaction> payments = new ArrayList<>();
    private final List<DomainEvent> domainEvents = new ArrayList<>();

    // State transitions enforce invariants
    public void acknowledge(ClaimHandler handler, LocalDate acknowledgeBy) {
        if (this.status != ClaimStatus.REGISTERED)
            throw new InvalidClaimStateException(this.reference, this.status, ClaimStatus.ACKNOWLEDGED);
        this.status = ClaimStatus.ACKNOWLEDGED;
        this.assignedHandler = handler;
        domainEvents.add(new ClaimAcknowledged(this.reference, handler, acknowledgeBy));
    }

    public void setReserve(MonetaryAmount amount, String justification, ClaimHandler authorisedBy) {
        if (!authorisedBy.canAuthoriseReserve(amount))
            throw new InsufficientAuthorityException(authorisedBy, amount);
        var previous = this.reserve;
        this.reserve = new Reserve(amount, Instant.now(), authorisedBy);
        domainEvents.add(new ReserveUpdated(this.reference, previous, this.reserve));
    }

    public void authorisePayment(MonetaryAmount amount, ClaimHandler authorisedBy) {
        if (amount.isGreaterThan(this.reserve.amount()))
            throw new PaymentExceedsReserveException(amount, this.reserve.amount());
        if (!authorisedBy.canAuthorisePayment(amount))
            throw new InsufficientAuthorityException(authorisedBy, amount);
        var payment = new PaymentTransaction(UUID.randomUUID(), amount, PaymentStatus.AUTHORISED, authorisedBy);
        this.payments.add(payment);
        domainEvents.add(new PaymentAuthorised(this.reference, payment));
    }
}
```

---

## Reserve Management Pattern

```java
// Reserves must be set at FNOL and updated as information develops
public class ReserveCalculationService {

    public MonetaryAmount calculateInitialReserve(ClaimType claimType, LossEvent loss) {
        return switch (claimType) {
            case MOTOR_OWN_DAMAGE -> estimateFromVehicleAge(loss.vehicle(), loss.damageDescription());
            case MOTOR_THIRD_PARTY_LIABILITY -> TPL_INITIAL_RESERVE;   // flat reserve until assessment
            case PROPERTY_BUILDINGS -> estimateFromSumInsured(loss.policy().buildingsSum(), 0.15);
            case EMPLOYERS_LIABILITY -> EL_INITIAL_RESERVE;
        };
    }

    // Ibnr (Incurred But Not Reported) — actuarial reserve for unreported tail
    public MonetaryAmount calculateIbnrReserve(ClaimType type, LocalDate accidentDate) {
        var developmentFactor = ibnrFactorRepository.find(type, YearMonth.from(accidentDate));
        return developmentFactor.apply(totalPaidToDate(type, accidentDate));
    }
}
```

---

## Fraud Indicators Pattern

```java
@Component
public class ClaimFraudIndicatorService {

    public FraudScore score(Claim claim) {
        var indicators = new ArrayList<FraudIndicator>();

        // Temporal indicators
        if (isRecentlyIncepted(claim.policy())) indicators.add(FraudIndicator.EARLY_CLAIM);
        if (isRenewalAdjacent(claim.lossEvent().date(), claim.policy())) indicators.add(FraudIndicator.RENEWAL_ADJACENT);

        // Behavioural indicators
        if (hasMultipleRecentClaims(claim.policy().holderId(), 3)) indicators.add(FraudIndicator.MULTIPLE_CLAIMS);
        if (isKnownLinkedParty(claim.thirdParty())) indicators.add(FraudIndicator.KNOWN_LINKED_PARTY);

        // Amount indicators
        if (claim.reserve().amount().isGreaterThan(LARGE_LOSS_THRESHOLD)) indicators.add(FraudIndicator.LARGE_LOSS);

        return FraudScore.calculate(indicators);
    }
}
```

---

## Subrogation Workflow

After payment, check recovery potential:

```java
public class SubrogationAssessment {
    private final ClaimReference claimRef;
    private final MonetaryAmount totalPaid;
    private final RecoveryPotential recoveryPotential;   // HIGH / MEDIUM / LOW / NONE

    // Third-party liability recovery
    // Supplier recovery (defective product)
    // Previous insurer recovery (late-reported policy transfer)
}
```

---

## Key Business Rules

| Rule | Detail |
|---|---|
| Reserve ≥ paid | Reserve must always cover total authorised payments |
| Authority matrix | Payment authority by grade: Handler <£5k, Manager <£25k, Director <£100k, Board above |
| SLA compliance | Acknowledge within 24h, assign handler within 48h, settlement offer within 90 days (UK FCA requirement) |
| Large loss notification | Claims >£100k must notify reinsurer and senior management within 24h |
| Legal involvement | Any claim involving solicitors must be escalated to legal team |
| Fraud hold | Claims with HIGH fraud score suspended for specialist review before any payment |
| FNOL capture | Minimum required at FNOL: date of loss, location, description, policy number |
