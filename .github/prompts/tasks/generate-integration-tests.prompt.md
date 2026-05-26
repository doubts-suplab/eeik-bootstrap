---
mode: "ask"
description: "Generate a Spring Boot integration test using @SpringBootTest or Testcontainers"
---

## Objective

Generate a complete Spring Boot integration test class that validates a feature end-to-end through the full application stack — including real HTTP handling, database persistence, and external service interactions (mocked where necessary). Use Testcontainers for database dependencies.

---

## Instructions to Copilot

1. Determine the integration test scope:
   - **API-level:** Use `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate` or `WebTestClient`
   - **Repository-level:** Use `@DataJpaTest` + Testcontainers for real DB
   - **Full slice:** Use `@SpringBootTest` with Testcontainers for DB and `@MockBean` for external services
2. Configure Testcontainers for the database:
   - PostgreSQL: `PostgreSQLContainer<>` with `@DynamicPropertySource`
   - DB2: `Db2Container<>` with `@DynamicPropertySource`
3. Use `@Sql` annotations to set up and tear down test data, or use a `DatabaseCleanup` utility
4. Test at least:
   - **Happy path** — the main success scenario
   - **Not found** — requesting a non-existent resource returns 404/empty
   - **Validation error** — invalid input returns 422 with problem detail
   - **Authorization** — unauthenticated request returns 401 (if security is active)
5. For REST endpoint tests, assert on HTTP status, response body structure, and `Content-Type`
6. Name tests: `featureUnderTest_scenario_expectedResult`
7. Apply Google Java Style: 2-space indent, 100-char limit
8. Use `@TestMethodOrder(MethodOrderer.OrderAnnotation.class)` only if test order matters — prefer independent tests

---

## Input

Provide:
- **The feature to test** — controller class, endpoint path, or use case description
- **Database platform** — PostgreSQL, DB2, H2
- **Authentication mechanism** — JWT, Basic Auth, or none
- **External services** — anything that must be mocked (payment gateway, messaging, etc.)

---

## Output

1. **Complete integration test file** — all imports, `@SpringBootTest` config, Testcontainers setup, `@DynamicPropertySource`, all test methods
2. **SQL test data scripts** — `src/test/resources/sql/test-data.sql` if needed
3. **File path** — `src/test/java/{package}/{FeatureName}IT.java`
4. **Run instruction** — Maven command to run only integration tests: `mvn failsafe:integration-test -Pintegration-tests`

---

## Quality Gates

- [ ] Uses Testcontainers for real database (not H2 unless H2 is the production database)
- [ ] Each test method is independent — no shared mutable state
- [ ] `@DynamicPropertySource` correctly wires container properties to Spring
- [ ] Each test asserts on HTTP status AND response body content
- [ ] External service calls are mocked via `@MockBean` — test does not call real third-party APIs
- [ ] File compiles and the Testcontainers dependency is available on the test classpath
