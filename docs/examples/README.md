# Examples

End-to-end project examples showing EEIK applied to real project types.

---

## Contents

| Example | Domain | Stack | Type |
|---------|--------|-------|------|
| [insurance-modernization/](insurance-modernization/end-to-end-walkthrough.md) | Insurance | IBM i + Java 21 + AWS | Modernization |

---

## How to Use These Examples

Each example is a complete walkthrough that shows:

1. The discovery questions answered during `/bootstrap`
2. The resulting `project-manifest.yaml`
3. The capability packs selected
4. The governance profile applied
5. The generated repository structure
6. The agents activated

Use these as reference when running `/bootstrap` on a similar project — the manifest structures and capability selections can be adapted directly.

---

## Planned Examples

The following examples are planned for future addition:

| Example | Domain | Stack | Type |
|---------|--------|-------|------|
| `java-microservices/` | Generic | Java 21 + Spring Boot + AWS | Greenfield |
| `aws-serverless/` | Generic | Lambda + API Gateway + DynamoDB | Greenfield |
| `agent-platform/` | AI | LangGraph + Bedrock + AWS | AI Platform |
| `ibmi-modernization/` | IBM i | RPG IV + Java 21 | Modernization |

---

## Contributing an Example

To add a new example:

1. Run a real `/bootstrap` session and save the outputs
2. Document the manifest and selected capabilities
3. Include the generated repository structure
4. Note any deviation from the default generation and why
5. Add the example to the index in this README
