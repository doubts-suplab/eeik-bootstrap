# Belgium Insurance Compliance Standard

Regulatory basis: FSMA | NBB | Wet Verzekeringen 2014 | IDD | PRIIPs | Solvency II | GDPR

---

## Non-Negotiable Compliance Rules

| # | Rule | Authority | Consequence of breach |
|---|------|-----------|----------------------|
| B01 | PRIIPs KID produced and current before any Branch 23 sale | FSMA | Product withdrawal, fine |
| B02 | Demands & Needs recorded for every policy sale | IDD / FSMA | Administrative sanction |
| B03 | FSMA intermediary number validated before commission | FSMA | Commission claw-back |
| B04 | TOB 2% collected on every Branch 23 premium and remitted monthly | FPS Finance | Tax penalty + interest |
| B05 | Withholding tax (30%) calculated and withheld on Branch 21 early surrender | FPS Finance | Tax penalty |
| B06 | Datassur query mandatory before writing new RC Auto policy | Belgian law | Void policy risk |
| B07 | Health data (for Life underwriting) treated as Article 9 GDPR special category | GDPR | Supervisory fine up to €20M |
| B08 | Policy documents in correct language per region | Wet Taalgebruik | Unenforceable contract |
| B09 | Complaint response within 30 days; escalation path to Ombudsman documented | Ombudsman law | Regulatory escalation |
| B10 | Solvency II SCR calculation reviewed quarterly; NBB notified if SCR <100% | Solvency II / NBB | Supervisory intervention |

---

## Data Classification (Belgian Insurance Context)

| Data category | Examples | Handling requirement |
|---|---|---|
| Ordinary personal data | Name, address, policy number | Standard GDPR |
| Financial personal data | Account number, premium amounts, claims | Contractual basis; 10-year retention |
| Special category — health | Medical questionnaires, disability claims | Explicit consent; strict access control; anonymise for analytics |
| Special category — criminal | Fraud history, court judgments | Legitimate interest basis; legal team approval |
| Sensitive product data | Branch 23 fund selections, investment profiles | MiFID suitability; restricted access |

---

## TOB (Taxe sur les Opérations de Bourse) — Branch 23

```
Rate: 2.00% on each premium payment
Taxable base: gross premium paid by policyholder
Remittance: monthly to FPS Finance, by 20th of following month
Reporting: annual TOB return
Exemptions: institutional investors, pension funds (specific conditions)

Calculation example:
  Premium paid:    €10,000
  TOB (2%):        €200
  Net invested:    €9,800

System requirement:
  TOB must be calculated at point of premium receipt
  Recorded separately in accounts
  Reconciled monthly before remittance
```

---

## Withholding Tax (Roerende Voorheffing) — Branch 21

```
Rate: 30% on deemed return
Only applies when:
  - Policy surrendered or matured
  - AND less than 8 years since first premium, OR age < 60

Deemed return calculation:
  Assumed annual return: 4.75%
  Tax base = Σ premiums paid × 4.75% × years held
  Tax = Tax base × 30%

Exempt when ALL of:
  - Policy held ≥ 8 years
  - Policyholder ≥ 60 years at time of payment
  - No partial surrenders in first 8 years

System requirement:
  Track first premium date per policy (immutable)
  Track all premium dates and amounts
  Calculate RV at surrender/maturity
  Issue tax certificate (fiscale fiche) to policyholder
  Report to FPS Finance (belcotax-on-web)
```

---

## Solvency II Technical Provisions

```
Life Technical Provisions:
  Best Estimate Liability (BEL):
    - Discount future cash flows at risk-free rate (EIOPA term structure)
    - Expenses: include contract boundary expenses
    - Lapses: apply experience-based lapse rates
    - Mortality: use Belgian mortality tables (MR / FR tables)

  Risk Margin:
    - Cost of Capital: 6% of SCR for non-hedgeable risks
    - Project SCR forward to run-off

P&C Technical Provisions:
  Premium provisions: unearned premium + unexpired risk
  Claims provisions: IBNR + case reserves + ULAE

NBB reporting:
  QRT (Quantitative Reporting Templates): quarterly submission
  SFCR (Solvency and Financial Condition Report): annual public disclosure
  RSR (Regular Supervisory Report): annual to NBB (confidential)
```

---

## IDD Target Market Assessment

Every new product must document:

```yaml
target_market:
  product: "Branch 23 Unit-Linked Policy"
  positive_target:
    investor_type: [retail, professional]
    knowledge_experience: [informed, advanced]    # not basic
    financial_situation:
      loss_bearing_capacity: can_bear_some_losses
      min_investment_horizon_years: 5
    risk_tolerance: [medium, medium_high, high]
    objectives: [capital_growth, long_term_saving]
  negative_target:
    - investors_needing_capital_guarantee
    - investors_with_horizon_under_5_years
    - investors_unable_to_bear_investment_losses
  distribution_channels: [face_to_face, online_with_advice]
  review_trigger: material_change_or_annual
```
