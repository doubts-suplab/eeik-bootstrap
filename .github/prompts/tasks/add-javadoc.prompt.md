---
mode: "ask"
description: "Add complete Javadoc to all public and protected members in a Java class"
---

## Objective

Add complete, meaningful Javadoc to every `public` and `protected` class, method, field, and constructor in the provided Java class. Javadoc must describe the business purpose — not just restate the method signature.

---

## Instructions to Copilot

1. Add a **class-level Javadoc** describing:
   - The class's single responsibility
   - Its layer (service, controller, repository, domain entity, DTO)
   - Any key collaborators or dependencies
2. Add **method-level Javadoc** for every `public` and `protected` method:
   - First sentence: what the method does (active voice: "Retrieves", "Creates", "Validates")
   - `@param` for every parameter — describe the meaning, not just the type
   - `@return` for every non-void method — describe what is returned and when it may be empty
   - `@throws` for every checked exception AND significant unchecked exceptions (e.g., `EntityNotFoundException`)
3. Add **field-level Javadoc** for `public` and `protected` fields (rare in well-designed code — use `/** */` inline)
4. Do NOT add Javadoc to:
   - Private methods (use inline comments sparingly if the logic is non-obvious)
   - Override methods where the parent already has Javadoc (use `{@inheritDoc}` instead)
   - Self-explanatory getters/setters on POJOs (e.g., `getId()`, `setName()`)
5. Use `{@code ...}` for inline code references in descriptions
6. Use `{@link ClassName}` or `{@link ClassName#methodName}` for type/method references
7. Do not use `@author` or `@since` tags — these are managed by version control
8. Apply Google Java Style: Javadoc text starts immediately after `/**`, sentences end with periods

---

## Input

Paste the Java class that needs Javadoc added.

---

## Output

The complete Java class with Javadoc added. Use a `### Changed` section to list which members received new Javadoc:

```markdown
### Javadoc Added

| Member | Type | Notes |
|--------|------|-------|
| `OrderService` | Class | Added class-level description and responsibility |
| `findById(UUID)` | Method | Added @param, @return, @throws OrderNotFoundException |
| `createOrder(CreateOrderRequest)` | Method | Added full Javadoc with business context |
```

---

## Quality Gates

- [ ] Every `public` method has `@param`, `@return` (if non-void), and `@throws` (if applicable)
- [ ] Class-level Javadoc present and meaningful
- [ ] No Javadoc that merely restates the signature ("Returns the id" → instead: "Returns the unique identifier assigned at creation")
- [ ] `{@link}` and `{@code}` used for references instead of plain text
- [ ] Override methods use `{@inheritDoc}` rather than duplicated documentation
