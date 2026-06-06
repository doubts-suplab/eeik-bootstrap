# /coverage-report — Coverage Analysis with Targeted Test Stubs

Analyse JaCoCo or Istanbul coverage and produce targeted tests to meet thresholds.

## Usage

```
/coverage-report
/coverage-report src/main/java/com/example/order/
/coverage-report src/app/orders/
```

## What This Command Does

### Java (JaCoCo)
1. Activates the `jacoco-coverage-tester` agent
2. Reads the JaCoCo XML or HTML report from `target/site/jacoco/`
3. Identifies classes below the 80% line / 70% branch threshold
4. Generates targeted JUnit 5 tests for the uncovered paths
5. Focuses on business logic — skips DTOs, config classes, and generated code

### Angular (Istanbul)
1. Activates the `angular-coverage-checker` agent
2. Reads the Istanbul `lcov.info` from `coverage/`
3. Identifies components and services below the 80% statement / 70% branch threshold
4. Generates targeted Jasmine specs for the uncovered branches

## Coverage Thresholds

| Language | Metric | Minimum |
|----------|--------|---------|
| Java | Line coverage | 80% |
| Java | Branch coverage | 70% |
| Angular | Statement coverage | 80% |
| Angular | Branch coverage | 70% |

## Output

```
## Coverage Report: {module/package}

### Below Threshold

| Class | Line % | Branch % | Gap |
|-------|--------|----------|-----|
| OrderService | 74% | 62% | 6% line, 8% branch |
| PaymentProcessor | 68% | 55% | 12% line, 15% branch |

### Generated Tests

For each class below threshold, produces:
- Method-level test stubs for uncovered paths
- Specific test cases for uncovered branches (null checks, exception paths, conditional branches)
- Complete, compilable test class ready to run
```

## Running Coverage Locally

### Java
```bash
./mvnw verify -Pci
# Report at: target/site/jacoco/index.html
```

### Angular
```bash
ng test --code-coverage --watch=false
# Report at: coverage/lcov.info
```

## Notes

- Prioritise testing business logic — do not write tests purely to inflate coverage metrics
- Focus on branches that represent real failure scenarios (null inputs, empty collections, exception paths)
- Coverage is a floor, not a target — aim for meaningful tests, not high percentages achieved with trivial tests
