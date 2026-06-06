# /estimate — Produce a P50/P80/P90 Effort Estimate

Produce a bottom-up effort estimate for a feature, epic, or technical task.

## Usage

```
/estimate "Add multi-currency support to the checkout flow including FX rate fetch, display, and order storage"
```

## What This Command Does

1. Activates the `estimator` agent
2. Decomposes the feature into implementable tasks
3. Assigns complexity ratings (Low / Medium / High) to each task
4. Calculates raw hours per task using reference ranges
5. Produces P50 / P80 / P90 estimates in human days
6. Surfaces risks and assumptions that could invalidate the estimate

## Formula

```
Human Days = Σ Raw Hours ÷ 6.4
```

Where `6.4 = 8 hours/day × 80% efficiency`

| Scenario | Multiplier | Use For |
|----------|------------|---------|
| P50 | ×1.0 | Sprint planning baseline |
| P80 | ×1.3 | Sprint commitment |
| P90 | ×1.6 | Release planning buffer |

## Output Format

The command produces:
- A list of assumptions (if wrong, the estimate is invalid)
- A task breakdown table with raw hours per task
- A summary table with P50 / P80 / P90 in human days and calendar days
- A list of risks and recommended spikes for high-uncertainty areas

## Tips for Better Estimates

- The more context you provide, the more accurate the decomposition:
  - Existing data model (does it need schema changes?)
  - Integration points (third-party APIs? Kafka events?)
  - Test requirements (unit only? integration tests? E2E?)
  - Team familiarity with the technology domain
- For large epics (>20 human days P50), request separate estimates per sub-feature
- High uncertainty areas should be time-boxed as spikes before committing
