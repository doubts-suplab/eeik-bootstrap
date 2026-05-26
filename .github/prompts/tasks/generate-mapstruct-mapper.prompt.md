---
mode: "ask"
description: "Generate a MapStruct mapper interface between two given Java classes"
---

## Objective

Generate a MapStruct mapper interface that maps between two provided Java classes (entity ↔ DTO, source ↔ target). The mapper is Spring-managed, handles field name mismatches, type conversions, and nested object mappings.

---

## Instructions to Copilot

1. Declare the mapper as: `@Mapper(componentModel = "spring")`
2. For each mapping method, annotate with `@Mapping` for:
   - **Field name differences** — source field name differs from target field name
   - **Type conversions** — `Long` ↔ `String`, `LocalDate` ↔ `String`, `BigDecimal` ↔ `String`
   - **Nested object mappings** — map inner objects by reference or by value
   - **Ignored fields** — sensitive or computed fields that must not be copied
3. Generate these mapping methods as needed:
   - `TargetType toTarget(SourceType source)` — single object mapping
   - `List<TargetType> toTargetList(List<SourceType> sources)` — list mapping
   - `void updateFromRequest(RequestDto request, @MappingTarget Entity entity)` — for update operations
4. For `@MappingTarget` update methods: only map fields present in the request — never overwrite audit fields (`createdAt`, `createdBy`)
5. Apply Google Java Style (2-space indent)
6. Add Javadoc on the interface describing what it maps

---

## Input

Provide:
- **Source class** — paste the full class or list the fields
- **Target class** — paste the full class or list the fields
- **Field mapping notes** — list any field name differences, type conversions, or fields to ignore

---

## Output

```java
package com.example.order.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;

/**
 * Maps between {@link Order} entity and order DTOs.
 *
 * <p>Spring-managed mapper; inject via constructor: {@code private final OrderMapper orderMapper}.
 */
@Mapper(componentModel = "spring")
public interface OrderMapper {

  @Mapping(source = "customer.id", target = "customerId")
  @Mapping(source = "customer.name", target = "customerName")
  @Mapping(target = "lineItemCount", expression = "java(order.getLineItems().size())")
  OrderResponseDto toResponseDto(Order order);

  List<OrderResponseDto> toResponseDtoList(List<Order> orders);

  @Mapping(target = "id", ignore = true)
  @Mapping(target = "createdAt", ignore = true)
  @Mapping(target = "status", constant = "PENDING")
  Order toEntity(CreateOrderRequestDto request);

  @Mapping(target = "id", ignore = true)
  @Mapping(target = "createdAt", ignore = true)
  void updateFromRequest(UpdateOrderRequestDto request, @MappingTarget Order order);
}
```

Include a mapping summary table:

```markdown
### Mapping Summary

| Source Field | Target Field | Conversion | Notes |
|-------------|-------------|-----------|-------|
| `customer.id` | `customerId` | Nested → flat | |
| `lineItems.size()` | `lineItemCount` | Expression | |
| — | `id` | Ignored | Set by persistence |
| — | `createdAt` | Ignored | Set by audit |
```

---

## Quality Gates

- [ ] `@Mapper(componentModel = "spring")` present
- [ ] All field mismatches covered with `@Mapping(source = ..., target = ...)`
- [ ] Audit fields (`id`, `createdAt`, `createdBy`) marked `ignore = true` on create/update mappings
- [ ] `@MappingTarget` used for update operations (not a new object)
- [ ] Mapping summary table produced
- [ ] No unmapped target properties that would cause a compile warning without explicit `ignore = true`
