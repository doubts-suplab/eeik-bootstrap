# /review-java — Java Code Review

Activate `java-code-reviewer` and run a standards-based review on Java code.

## Usage
```
/review-java
/review-java src/main/java/com/example/OrderService.java
```

## What This Command Does
1. Reads the target file(s) — defaults to changed files in current branch
2. Applies java-pack review checklist against all mandatory standards
3. Produces BLOCKING / MAJOR / MINOR findings
4. Issues APPROVE or REQUEST CHANGES verdict
