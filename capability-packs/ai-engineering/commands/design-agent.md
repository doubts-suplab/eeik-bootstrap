# /design-agent — Design a New Agent

Activate `ai-architect` and produce a complete agent definition.

## Usage
```
/design-agent "Settlement Optimization Specialist — analyses insurance claims and recommends settlement amounts"
```

## What This Command Does
1. Elicits: purpose, domain, responsibilities, inputs, outputs, constraints, tools
2. Applies agent-standard checklist
3. Produces agent definition using `templates/agent-definition.md.template`
4. Identifies evaluation dataset structure
5. Flags governance requirements (regulated domain, PII, financial decisions)

## Output
- `agents/{agent-name}.md`
- `agents/evaluation/{agent-name}/dataset.yaml` (skeleton)
