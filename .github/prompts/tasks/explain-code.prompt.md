---
mode: "ask"
description: "Explain any code block in plain English — COBOL-aware, stack-aware"
---

## Objective

Produce a clear, plain-English explanation of the provided code block. The explanation must be accurate, structured, and useful to both developers and non-developers reviewing the logic. This prompt is stack-aware: COBOL programs get their mainframe-specific constructs explained, Java gets design pattern and Spring context, Angular gets component lifecycle and reactive flow.

---

## Instructions to Copilot

1. Identify the language and framework from the code
2. Produce a **three-level explanation:**
   - **Level 1 — What it does** (1 paragraph, plain English, no jargon — suitable for a business analyst)
   - **Level 2 — How it works** (structured walkthrough, section by section or method by method)
   - **Level 3 — Key technical points** (design decisions, patterns used, gotchas, non-obvious behaviour)
3. For **COBOL code:**
   - Explain each division and paragraph
   - Identify and explain all `EXEC SQL` blocks
   - Identify all `EXEC CICS` interactions
   - Note the Java equivalent for each significant construct
   - Flag any `ALTER`, `GO TO`, `PERFORM THRU` for extra explanation
4. For **Java code:**
   - Explain the class responsibility and its layer (controller, service, repository, domain)
   - Identify Spring annotations and their effect
   - Explain transaction boundaries
   - Flag any subtle behaviour (lazy loading, proxy behaviour, static state)
5. For **Angular code:**
   - Explain the component lifecycle hooks invoked
   - Explain Observable/Signal subscriptions
   - Explain data flow between parent and child components
6. Produce a **data flow diagram** in plain text or Mermaid if the code has a complex multi-step flow
7. List any **side effects** — database writes, external calls, event emissions, file I/O

---

## Input

Paste the code to explain, or reference the open file. Indicate the audience if relevant:
- "Explain for a Java developer unfamiliar with COBOL"
- "Explain for a business analyst"
- "Explain for a junior developer new to Spring Security"

---

## Output

```markdown
## Code Explanation — {ClassName / ProgramName}

### What It Does
<Plain English, 1 paragraph, jargon-free>

### How It Works

#### {Section / Method / Paragraph Name}
<Step-by-step walkthrough>

### Key Technical Points
- <Design decision or gotcha #1>
- <Spring/COBOL-specific behaviour to know>

### Side Effects
- Writes to: {table / file / queue}
- Calls: {external service / CICS transaction}
- Events emitted: {event name}

### Java Equivalent (for COBOL only)
<What this would look like in Java>
```

---

## Quality Gates

- [ ] Level 1 explanation is readable by a non-developer
- [ ] All significant code paths are explained — not just the happy path
- [ ] For COBOL: all `EXEC SQL` and `EXEC CICS` blocks are explained
- [ ] Side effects are completely listed
- [ ] No unexplained jargon in Level 1
