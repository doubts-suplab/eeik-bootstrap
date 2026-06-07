# /review-infrastructure — AWS Infrastructure Review

Activate `cloud-security-reviewer` and run a security + compliance review on CDK/Terraform code.

## Usage
```
/review-infrastructure
/review-infrastructure infrastructure/stacks/AppStack.ts
```

## What This Command Does
1. Reads CDK/Terraform files
2. Applies aws-pack security checklist
3. Checks tagging compliance
4. Produces CRITICAL/HIGH/MEDIUM findings
5. Issues APPROVE or BLOCK verdict
