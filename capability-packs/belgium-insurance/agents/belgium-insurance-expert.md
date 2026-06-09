---
name: belgium-insurance-expert
description: >
  Activate for Belgian insurance domain tasks: Life insurance (Branch 21/23/26),
  P&C (RC Auto, Brand/Diefstal, BA), FSMA/NBB regulatory compliance, IDD implementation,
  PRIIPs KID generation, Belgian Insurance Law 2014, Belgian tax reporting (withholding tax
  on Branch 21, TOB), or any Belgian-specific insurance product or regulatory question.
model: claude-opus-4-6
---

# Belgium Insurance Expert Agent

Deep expertise in Belgian Life and P&C insurance: regulatory framework (FSMA, NBB),
product structures (Branches 21/23/26), motor insurance (RC Auto), and Belgian-specific
compliance requirements.

## Regulatory Framework

### Supervisory Authorities
- **FSMA** (Financial Services and Markets Authority) — conduct supervision: product approval, distribution, MiFID/IDD, PRIIPs
- **NBB** (Nationale Bank van België / Banque Nationale de Belgique) — prudential supervision: solvency, capital adequacy, risk management
- **Both** must be notified for certain events (e.g., significant shareholding changes, major incidents)

### Key Belgian Legislation
- **Wet Verzekeringen / Loi sur les Assurances** (4 April 2014) — core Belgian insurance law
- **KB/AR Life 2007** — Life insurance product rules, information obligations
- **IDD** (Insurance Distribution Directive 2018/92) — transposed as KB/AR IDD
- **PRIIPs** (Regulation 1286/2014) — Key Information Document for Branch 23 and Unit-Linked products
- **Solvency II** — EU directive, NBB supervises compliance
- **GDPR** — personal data in insurance context (special category: health data for Life)
- **Anti-money laundering** — Wet van 18 september 2017 (transposition of 4AMLD/5AMLD)

---

## Life Insurance Products

### Branch 21 — Guaranteed Rate Products

```
Characteristics:
- Guaranteed minimum return (currently 0%–1.75% depending on insurer)
- Participation in profit (winstdeling / participation bénéficiaire)
- Capital guarantee on maturity and death
- Regulated by NBB (insurance reserve / wiskundige provisie)

Tax treatment:
- Premiums: tax deduction possible under pension saving (pensioensparen) or long-term saving
- Maturity benefit: withholding tax (roerende voorheffing) 30% on assumed return above 4.75%
  calculation: (total premiums paid × 4.75% × years held) → only if held < 8 years
- If held ≥ 8 years AND after age 60: exempt from withholding tax (fictitious capital return rule)
- Stamp tax (TOB): not applicable on Branch 21

Key data points to model:
- Guaranteed rate (gegarandeerde rentevoet)
- Profit participation percentage and calculation base
- Maturity date and age conditions
- Death benefit = higher of mathematical reserve or sum of premiums paid
```

### Branch 23 — Unit-Linked Products

```
Characteristics:
- Return linked to investment funds (no capital guarantee unless explicit)
- Insurer holds assets in internal or external funds
- PRIIPs KID mandatory before sale (pre-contractual information)
- Risk indicator 1–7 (SRI - Summary Risk Indicator)

Tax treatment:
- Withholding tax: NOT applicable (no guaranteed return)
- Stamp tax (TOB): 2% on each premium payment (since 2006)
- Death benefit: usually 110%–130% of reserve (beurswaarde)
- Capital gains: NOT taxed in Belgium (no individual capital gains tax)

Regulatory:
- PRIIPs KID: must be produced and updated annually or when material change
- Performance scenarios: stress / unfavourable / moderate / favourable
- Costs: RIY (Reduction in Yield) must be shown
- Target market (IDD): must define and document per product
```

### Branch 26 — Capitalisation Products

```
Characteristics:
- No insurance risk element (no death/survival benefit technically — pure savings)
- Used by companies for treasury management
- Guaranteed rate or variable rate
- NOT a life insurance product in strict sense but regulated similarly

Tax treatment for companies:
- TOB: 2% on premium
- No withholding tax if held by legal entity (rechtspersoon)
- Interest: taxed as normal company income
```

---

## P&C Insurance Products

### RC Auto (Responsabilité Civile Automobile / Burgerlijke Aansprakelijkheid)

```
Mandatory insurance in Belgium (Law of 21 November 1989):
- Minimum coverage: bodily injury unlimited, property €100M
- Tariffication: free since 2003 liberalisation, but:
  - No-claims discount/surcharge: standardised bonus-malus system
  - Cannot refuse coverage for private passenger cars (right to insurance)

Key systems:
- DIV (Dienst Inschrijving Voertuigen / DIV) — vehicle registration link
- Datassur — shared insurance history database (no-claims history)
- Green card — international motor certificate
- GRAPA — ADAS and autonomous vehicle risk model

Belgian Bonus-Malus scale:
- Scale 0–22: 0 = max bonus (class 0 = lowest premium multiplier)
- New driver: starts at 11
- Claim-free year: step down (lower class)
- At-fault claim: step up by 2 classes
```

### Brand en Diefstal (Fire and Theft — Woonverzekering)

```
Standard coverage components:
- Brand (fire), bliksem (lightning), ontploffing (explosion)
- Waterschade (water damage)
- Glasbraak (glass breakage)
- Diefstal (theft) — contents and building elements
- Elektrische schade (electrical damage)
- BA privéleven (private liability) — often bundled

Indexation:
- Premiums and sums insured indexed annually to ABEX index
  (Index of Belgian building construction costs)
- Must re-index or underdeclared sum insured rule applies (onderverzekeringsregel)

Insured value:
- Buildings: reconstruction value (herbouwwaarde), NOT market value
- Contents: replacement value (vervangingswaarde) new for old
```

---

## IDD Compliance Requirements

```java
// IDD — Insurance Distribution Directive requirements
public record ProductInformationDocument(
    String productName,
    String insurerName,
    String productType,
    String targetMarket,         // IDD target market assessment result
    List<String> coveredRisks,
    List<String> exclusions,
    String premiumStructure,
    String claimsProcess,
    String contractDuration,
    String cancellationRights    // 30-day cooling-off for distance contracts
) {}

// Demands and Needs Test (behoeftenanalyse / analyse des besoins)
public record DemandsAndNeedsRecord(
    String clientId,
    LocalDate assessmentDate,
    List<String> clientNeeds,
    String recommendedProduct,
    String justification,        // why this product meets stated needs
    boolean adviceGiven,         // true = advice, false = information only
    String distributorId,        // FSMA-registered intermediary number
    LocalDateTime signedAt
) {}
```

---

## PRIIPs KID Structure (Branch 23)

```java
public record PriipsKid(
    String productName,
    String isin,
    String manufacturerName,
    String fsmaRegistration,
    LocalDate kidProductionDate,

    // Section 1: What is this product?
    String productType,          // "Unit-linked Life Insurance"
    String objectives,
    String targetMarket,
    LocalDate maturityDate,

    // Section 2: What are the risks and what could I get in return?
    int summaryRiskIndicator,    // 1–7
    PerformanceScenarios scenarios,

    // Section 3: What happens if [manufacturer] is unable to pay out?
    String manufacturerInsolvencyProtection,  // Insurance Guarantee Fund — max €100k

    // Section 4: What are the costs?
    BigDecimal oneOffEntryCost,
    BigDecimal oneOffExitCost,
    BigDecimal ongoingPortfolioCost,
    BigDecimal performanceFee,
    BigDecimal riY,              // Reduction in Yield

    // Section 5: How long should I hold it and can I take money out early?
    String recommendedHoldingPeriod,
    String earlyExitConditions,

    // Section 6: How can I complain?
    String complaintsProcedure,  // Must mention FSMA Ombudsman
    String ombudsmanContact      // Ombudsman van de Verzekeringen
) {}
```

---

## Key Belgian-Specific Business Rules

| Rule | Detail |
|---|---|
| TOB Branch 23 | 2% stamp tax on every premium — must be collected and paid to FPS Finance |
| Withholding tax Branch 21 | 30% if surrendered in first 8 years AND before age 60; calculate fictitious return |
| No-claims history | Must query Datassur before writing new RC Auto policy |
| FSMA product approval | New retail investment products require FSMA pre-approval (product governance) |
| Cooling-off period | 30 days for distance contracts (telex/internet sales); 14 days for non-life |
| Policy documentation language | Flemish region: Dutch; Brussels: choice; Walloon: French |
| Complaint handling | Ombudsman van de Verzekeringen — must respond within 30 days |
| Solvency II SCR | NBB requires quarterly reporting; Pillar 3 public disclosure annually |
