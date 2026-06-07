# /run-review — Run a Governance Review

Activate the appropriate reviewer agent and produce a structured governance review.

## Usage
```
/run-review architecture
/run-review security
/run-review prr
/run-review compliance
/run-review ai-governance
```

## What This Command Does
1. Reads the governance profile from `project-manifest.yaml`
2. Activates the appropriate reviewer agent
3. Reads the required artifacts for that review type
4. Produces a structured review report with CRITICAL/MAJOR/MINOR findings
5. Issues a verdict with conditions if applicable
6. Logs the decision to `.claude/memory/decisions.md`
