# Prompt Engineering Standard

**Pack:** ai-engineering-pack | **Version:** 1.0

---

## Prompt Structure

Every system prompt must contain these sections in order:

```
1. Role definition       — who/what the agent is
2. Capabilities          — what it can do
3. Constraints           — what it must never do (explicit negatives)
4. Input format          — what it expects
5. Output format         — what it produces (structure, schema, examples)
6. Tone                  — how it communicates
```

---

## Writing Effective Prompts

### Be Specific About Constraints
```
# ❌ Weak
Do not produce harmful content.

# ✅ Strong
Do not:
- Generate SQL queries that modify data (INSERT/UPDATE/DELETE)
- Access files outside the /workspace directory
- Call external APIs not in the approved tool list
- Include PII (names, emails, national IDs) in any response
```

### Define Output Format Precisely
```
# ✅ Good
Respond in this exact JSON structure:
{
  "recommendation": "APPROVE | REJECT | DEFER",
  "findings": [{ "severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "..." }],
  "rationale": "2-3 sentence explanation"
}
```

### Use Positive and Negative Examples
Provide at least one example of correct output and one of incorrect output for complex tasks.

---

## Prompt Version Control

- Store prompts in version-controlled files (`.md` or `.yaml`)
- Version prompts: `v1.0`, `v1.1`, `v2.0`
- Document changes in prompt changelog
- Never modify a production prompt without running evaluation first

---

## Prohibited Prompt Patterns

| Pattern | Risk |
|---------|------|
| "Do whatever the user asks" | No constraint — full jailbreak surface |
| Prompts containing actual secrets/keys | Secret leakage |
| "Use your best judgment" without criteria | Inconsistent, unpredictable output |
| Prompts > 10,000 tokens | Context window waste, latency |
