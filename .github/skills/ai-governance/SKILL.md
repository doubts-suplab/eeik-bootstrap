# AI Governance Skill

## Trigger

Use this skill when reviewing AI/ML systems for compliance, producing model cards, conducting bias assessments, or classifying systems under the EU AI Act.

## What This Skill Does

1. Classifies the AI system by EU AI Act risk tier (Unacceptable / High / Limited / Minimal)
2. Identifies data governance gaps (lineage, quality, bias sources)
3. Produces a model card covering intended use, limitations, and ethical considerations
4. Generates a pre-deployment AI governance checklist
5. Flags GDPR Article 22 exposure for automated decision-making

## Inputs Required

- Description of the AI system: purpose, inputs, outputs, affected users
- Training data sources and known characteristics
- Deployment context: who will use it, what decisions it supports
- Any existing evaluation metrics (accuracy, fairness metrics)

## Outputs Produced

- EU AI Act risk classification with rationale
- Model card in standard format
- AI risk register entry
- Pre-deployment governance checklist
- Identified gaps with remediation recommendations

## Standards Applied

See `.github/instructions/ai-governance.instructions.md`

## Related Agents

- `ai-governance-officer` — Claude Code agent for deep governance reviews
- `ai-engineer` — for technical AI system design
- `security-auditor` — for security aspects of AI systems
