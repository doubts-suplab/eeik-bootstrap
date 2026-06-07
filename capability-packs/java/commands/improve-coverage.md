# /improve-coverage — Improve Java Test Coverage

Activate `java-test-engineer` and produce targeted tests to improve coverage.

## Usage
```
/improve-coverage
/improve-coverage src/main/java/com/example/OrderService.java
```

## What This Command Does
1. Reads JaCoCo report (or runs `mvn test jacoco:report`)
2. Identifies uncovered methods and branches
3. Prioritises by business criticality
4. Produces complete test classes targeting gaps
5. Reports expected coverage delta
