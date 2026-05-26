---
mode: "ask"
description: "Generate a complete REST API: controller, service, DTO, repository, and OpenAPI annotations"
---

## Objective

Generate a complete, production-ready REST API implementation for a described resource. Produces the full vertical slice: controller, service interface + implementation, DTO records, JPA entity, repository interface, MapStruct mapper, and OpenAPI annotations.

---

## Instructions to Copilot

Generate all of the following artifacts for the described resource:

1. **DTO records** (Java 17+ records for Spring Boot; POJOs for legacy):
   - Request DTO: input validation annotations (`@NotNull`, `@Size`, `@Valid`)
   - Response DTO: all fields the caller needs, no internal IDs or sensitive fields
2. **JPA Entity** (Spring Boot) or JDBC-mapped class (legacy):
   - `@Entity`, `@Table(schema = "SCHEMA", name = "TABLE_NAME")`
   - Audit fields: `createdAt`, `updatedAt` via `@CreatedDate`, `@LastModifiedDate`
   - No bidirectional `@OneToMany` without `mappedBy` — prevent cartesian product fetches
3. **Repository Interface** (Spring Boot: `JpaRepository`; legacy: `JdbcTemplate` class)
4. **MapStruct Mapper Interface**:
   - `@Mapper(componentModel = "spring")`
   - Maps between Entity ↔ RequestDTO ↔ ResponseDTO
5. **Service Interface + Implementation**:
   - Constructor injection only
   - `@Transactional(readOnly = true)` on class, `@Transactional` on write methods
   - Returns `Optional<T>` for single lookups, `Page<T>` for lists
   - Throws domain exceptions (`ResourceNotFoundException`) — not Spring exceptions
6. **REST Controller**:
   - `@RestController`, `@RequestMapping("/api/v1/{resources}")`
   - `@Tag(name = "...")` and `@Operation(summary = "...")` from springdoc-openapi
   - `ResponseEntity<T>` with correct HTTP status codes (201 for POST, 204 for DELETE)
   - `@Valid` on `@RequestBody` parameters
   - Constructor injection only
7. **Exception class**:
   - `ResourceNotFoundException extends RuntimeException`
   - Used by service; handled by `@RestControllerAdvice` (reference `GlobalExceptionHandler` if it exists)
8. **Apply Google Java Style** throughout: 2-space indent, 100-char limit

---

## Input

Provide:
- **Resource name** — e.g., "Customer", "Order", "Invoice"
- **Fields** — list the fields the resource has (name, type, required/optional, constraints)
- **Operations needed** — which of: GET by ID, GET all (paginated), POST, PUT, DELETE, PATCH
- **Target module** — Spring Boot 3.x (Java 17/21) or legacy Spring MVC (Java 8/11)
- **Database schema name** — the DB2/PostgreSQL schema to use in `@Table`

---

## Output

Produce files in this order, each with its file path:

1. `{Resource}RequestDto.java` (or record)
2. `{Resource}ResponseDto.java` (or record)
3. `{Resource}.java` (entity)
4. `{Resource}Repository.java`
5. `{Resource}Mapper.java`
6. `{Resource}Service.java` (interface)
7. `{Resource}ServiceImpl.java`
8. `{Resource}Controller.java`
9. `{Resource}NotFoundException.java`

---

## Quality Gates

- [ ] All files compile together without modification
- [ ] Controller uses `ResponseEntity<T>` with correct HTTP status codes
- [ ] Service uses `@Transactional` on write methods
- [ ] All `@RequestBody` parameters annotated with `@Valid`
- [ ] OpenAPI annotations present on controller methods
- [ ] No `SELECT *` in any generated queries
- [ ] No `return null` in service methods — use `Optional` or throw
- [ ] Google Java Style applied to all files
