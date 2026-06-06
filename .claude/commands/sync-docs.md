# /sync-docs — Sync API Documentation Against OpenAPI Specs

Validate and synchronise API documentation against the current OpenAPI specification.

## Usage

```
/sync-docs
/sync-docs src/main/resources/openapi.yml
/sync-docs src/main/java/com/example/order/web/
```

## What This Command Does

1. Activates the `technical-writer` agent
2. Reads the current OpenAPI spec (from `src/main/resources/openapi.yml` or generated via Springdoc)
3. Compares spec against the actual controller code and annotations
4. Identifies gaps: undocumented endpoints, missing response codes, stale descriptions
5. Updates or generates OpenAPI annotation recommendations for missing documentation
6. Validates that spec examples match actual request/response shapes

## Validation Checks

| Check | What Is Verified |
|-------|----------------|
| Endpoint coverage | Every `@RestController` method has an `@Operation` annotation |
| Response codes | All possible HTTP response codes are documented |
| Request schema | `@Schema` annotations on all DTO fields |
| Examples | At least one request and one response example per endpoint |
| Error responses | RFC 7807 `ProblemDetail` documented for all error codes |
| Deprecated endpoints | `@Deprecated` methods have `deprecated: true` in the spec |

## Output

```
## API Documentation Sync Report

### Gaps Found

| Endpoint | Issue | Severity |
|----------|-------|---------|
| POST /orders | Missing @Operation summary | MAJOR |
| GET /orders/{id} | Response 404 not documented | MAJOR |
| PUT /orders/{id}/status | No request body example | MINOR |

### Recommendations
{Specific annotation additions for each gap}

### Stale Content
{Documented endpoints that no longer exist in code}
```

## Generating the OpenAPI Spec

If using Springdoc OpenAPI:
```bash
./mvnw spring-boot:run &
curl http://localhost:8080/v3/api-docs | python3 -m json.tool > openapi.json
```

Or configure static generation in the Maven build.

## Notes

- Run `/sync-docs` before each release to catch documentation drift
- API documentation is a first-class deliverable — treat stale docs as a bug
- OpenAPI specs should be committed to source control and reviewed in PRs like any code change
