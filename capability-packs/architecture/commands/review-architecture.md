# /review-architecture — Architecture Review

Activate the `arb-reviewer` agent and conduct a structured architecture review against EEIK standards.

## Usage
```
/review-architecture
/review-architecture docs/architecture/payment-service-architecture.md
```

## What This Command Does
1. Reads the architecture document (or prompts for input)
2. Evaluates against `standards/architecture-principles.md`, `standards/nfr-standard.md`, `standards/integration-standard.md`
3. Produces a structured review report with APPROVE / APPROVE WITH CONDITIONS / DEFER / REJECT recommendation
4. Lists specific findings with severity: BLOCKING / MAJOR / MINOR / SUGGESTION

## Output
- Review report printed to console
- Optionally: `docs/reviews/{service-name}-arch-review-{date}.md`
