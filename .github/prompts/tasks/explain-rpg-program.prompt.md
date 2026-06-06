# Explain RPG Program

Analyse and explain the following IBM i RPG IV / RPGLE program:

**Program:** $PROGRAM_NAME

## Instructions

1. Read the program source code
2. Identify the program type: batch, interactive (display file), or service program
3. Explain the business purpose in plain English
4. Document the data structures, file I/O, and calculation logic
5. Map IBM i data types to their Java equivalents

See `.github/instructions/ibmi.instructions.md` for IBM i standards.

## Output Format

```markdown
## RPG Program Analysis: {PROGRAM_NAME}

### Program Type
{batch / interactive / service program / module}

### Business Purpose
<!-- Plain-English description of what business function this program performs -->

### Data Structures

| DS Name | Field | IBM i Type | Precision | Java Equivalent | Business Meaning |
|---------|-------|-----------|-----------|----------------|-----------------|

### File I/O

| File | DDS Type | Access Mode | Key Fields | Business Role |
|------|---------|------------|------------|--------------|

### Business Rules (Extracted from Calculation Logic)

1. **{Rule Name}:** {Plain-English description of the rule}
   - Implemented at: {paragraph/subprocedure name}
   - Condition: {when does this rule apply}
   - Action: {what happens when the condition is met}

### External Calls

| Program/Procedure | Call Type | Purpose |
|-------------------|-----------|---------|

### Error Handling
<!-- How does this program handle errors? What happens when files are not found or I/O fails? -->

### Modernisation Notes
<!-- What aspects of this program would map easily to Java, and what are the challenges? -->
```
