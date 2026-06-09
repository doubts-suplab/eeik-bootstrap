# Strangler Fig Standard

**Applies To:** All modernization projects  
**Strategy:** Incrementally replace legacy functionality while keeping the legacy system running

---

## Core Principle

```
NEVER do a big-bang rewrite.
ALWAYS run legacy and modern in parallel.
ALWAYS prove modern works before routing traffic.
ALWAYS have a rollback plan before each wave cutover.
```

---

## Phase Model

```
Phase 1: COEXIST
  Legacy handles all traffic.
  New system built alongside — not yet receiving production traffic.
  Data sync established (CDC or dual-write).

Phase 2: SHADOW
  New system receives a copy of production traffic.
  Responses NOT returned to users — compared to legacy in background.
  Monitor for divergence.

Phase 3: CANARY
  New system handles 5% → 10% → 25% → 50% of traffic.
  Legacy handles the rest.
  Monitor error rates, latency, business accuracy.

Phase 4: CUTOVER
  New system handles 100% of traffic.
  Legacy in warm standby (not decommissioned yet).
  Monitor for 2–4 weeks.

Phase 5: DECOMMISSION
  Legacy removed after cutover stability confirmed.
  Database schemas migrated / retired.
```

---

## Wave Ordering Rules

1. **Leaf programs first** — programs with no outbound calls to other legacy programs
2. **High value, low complexity** — prove the pattern with easy wins before tackling complex core
3. **Business domains, not technical layers** — migrate complete bounded contexts, not horizontal layers
4. **Never split a bounded context across waves** — one context = one wave

---

## Rollback Criteria

Define rollback triggers BEFORE each wave cutover:

```
Auto-rollback if:
  - Error rate > 1% (vs legacy baseline of {n}%)
  - p99 latency > {threshold}ms (vs legacy {baseline}ms)
  - Any data consistency violation detected
  - Business metric deviation > 2% (e.g. order counts, payment totals)

Manual rollback if:
  - Business team reports functional difference vs legacy behaviour
  - On-call SRE declares P1 incident
```

---

## Legacy Adapter Pattern (Java)

```java
/**
 * Strangler Fig Facade — routes to modern or legacy implementation.
 * Remove condition when wave cutover is complete and legacy is decommissioned.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderCalculationFacade {

    private final ModernOrderCalculationService modernService;
    private final LegacyOrderCalculationAdapter legacyAdapter;
    
    @Value("${feature.modern-order-calculation:false}")
    private boolean useModernCalculation;

    public OrderCalculationResult calculate(OrderCalculationRequest request) {
        if (useModernCalculation) {
            log.info("Routing order calculation to modern service orderId={}", request.getOrderId());
            return modernService.calculate(request);
        }
        log.info("Routing order calculation to legacy adapter orderId={}", request.getOrderId());
        return legacyAdapter.calculate(request);
    }
}
```

The feature flag (`feature.modern-order-calculation`) is managed in AWS AppConfig or SSM Parameter Store — allows runtime switching without redeployment.
