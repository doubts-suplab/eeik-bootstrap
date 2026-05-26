---
mode: "ask"
description: "Generate a complete JUnit 5 unit test class for the selected or named Java class"
---

## Objective

Generate a complete, compilable JUnit 5 unit test class for a given Java class. The output is a fully functional test file with all imports, setup methods, and meaningful test cases covering happy paths, edge cases, and exception scenarios.

---

## Instructions to Copilot

1. Read the provided class carefully — identify every public method and its branching logic
2. Identify the dependencies that need to be mocked (constructor parameters, injected services)
3. Generate a test class using `@ExtendWith(MockitoExtension.class)` with `@Mock` and `@InjectMocks`
4. For each public method, generate:
   - **Happy path test** — the normal successful execution
   - **Not-found / null test** — when a looked-up entity does not exist
   - **Invalid input test** — when input is null, empty, negative, or out-of-range
   - **Exception path test** — when a dependency throws an exception
5. Use `@ParameterizedTest` + `@MethodSource` for any method with multiple valid input variants
6. Name every test method: `methodName_scenario_expectedResult`
7. Use AssertJ assertions exclusively — never `assertEquals` or `assertTrue`
8. Create a `TestFactory` inner class or static factory methods for test data objects — no raw `new` in test bodies
9. Apply Google Java Style formatting: 2-space indent, 100-char line limit, Egyptian braces
10. Add a brief Javadoc comment on the test class referencing the class under test

---

## Input

Provide one of the following:
- **Paste the full class source** in your message
- **Name the class** (`OrderService`, `CustomerController`) and ensure it is open in the editor

---

## Output

1. **Complete test file** — package declaration, all imports, class with `@ExtendWith`, all test methods
2. **File path** — where to save the test file: `src/test/java/{package}/{ClassName}Test.java`
3. **Coverage summary** — table of methods tested and scenarios covered
4. **Missing mocks** — list any dependencies that need to be added to the classpath if they are not already present

---

## Quality Gates

The output is acceptable only if:

- [ ] Every `@Test` method has at least one meaningful assertion on business outcome (not just mock verification)
- [ ] All happy paths covered
- [ ] All null/not-found paths covered
- [ ] At least one exception path covered per method that calls a dependency
- [ ] No `Thread.sleep()` — use `Awaitility` for async tests
- [ ] Google Java Style formatting applied
- [ ] File compiles without modification (all imports present, no undefined types)
