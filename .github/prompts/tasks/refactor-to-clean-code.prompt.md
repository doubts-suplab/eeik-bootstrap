---
mode: "ask"
description: "Refactor selected code applying SOLID principles, clean code rules, and Google Java Style"
---

## Objective

Refactor the provided code to comply with SOLID principles, clean code conventions, and Google Java Style Guide — without changing the observable behaviour. Every refactoring must be behaviour-preserving. If a refactoring requires an interface change (method signature, public API), flag it explicitly before making the change.

---

## Instructions to Copilot

Apply refactorings in this priority order:

1. **Extract methods** — any method longer than 20 lines should be decomposed into named private methods
2. **Single Responsibility** — if a class does more than one thing, propose the split (but do not split without asking if it changes the public API)
3. **Remove magic numbers** — replace numeric/string literals with named constants
4. **Replace null returns** — replace `return null` with `Optional<T>` or a domain exception
5. **Replace raw types** — `List` → `List<MyType>`, `Map` → `Map<String, MyType>`
6. **Replace empty catch blocks** — either log + rethrow, rethrow as domain exception, or add explanatory comment if truly intentional
7. **Add SLF4J logging** — at method entry (DEBUG) for service methods, WARN for recoverable errors, ERROR for exceptions
8. **Apply Java 17/21 idioms** (Spring Boot modules only):
   - Replace mutable DTOs with records
   - Replace `instanceof` + cast with pattern matching
   - Replace `switch` statement with `switch` expression
   - Replace `if (x != null)` chains with `Optional.ofNullable(x).map(...)`
9. **Apply Google Java Style formatting:**
   - 2-space indentation
   - 100-char line limit
   - Egyptian braces
   - `@Override` on all overriding methods
10. **Add Javadoc** on all public methods that do not have it

Do not:
- Change the public method signatures without flagging it
- Add new dependencies
- Change the class's domain responsibility
- Introduce abstractions that are not justified by the existing code

---

## Input

Paste the code to refactor directly in your message.

Specify:
- **Target Java version** — 8/11 (legacy) or 17/21 (Spring Boot)
- **Module context** — legacy Spring MVC or Spring Boot?

---

## Output

1. **Refactored code** — complete file, all imports, ready to copy-paste
2. **Refactoring summary** — table listing each change made and its rationale:

```markdown
| Change | Where | Rationale |
|--------|-------|-----------|
| Extracted `validateCustomerInput()` | Line 45–67 | Method was 35 lines; extraction improves readability |
| Replaced `null` return with `Optional` | `findById()` return type | Callers must handle absence explicitly |
| Added `CUSTOMER_NOT_FOUND_CODE = 404` constant | Class level | Magic number 404 appeared 3 times |
```

3. **API changes flagged** (if any):
```markdown
⚠️ API CHANGE: `findById()` return type changes from `Customer` to `Optional<Customer>`.
All callers must be updated. Proceed?
```

---

## Quality Gates

- [ ] Behaviour preserved — all existing tests still pass
- [ ] No magic numbers remain in the refactored code
- [ ] No methods longer than 20 lines in the output
- [ ] No empty catch blocks
- [ ] All public methods have Javadoc
- [ ] Google Java Style applied
- [ ] API changes explicitly flagged before implementation
