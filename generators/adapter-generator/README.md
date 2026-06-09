# Adapter Generator

Synthesises AI tool adapter files from the shared EEIK intelligence layer.

## What It Produces

| Adapter | Location | Tool |
|---------|----------|------|
| Kiro steering docs | `.kiro/steering/` | Amazon Kiro IDE |
| Kiro hooks | `.kiro/hooks/` | Amazon Kiro IDE |
| Codex manifest | `AGENTS.md` | OpenAI Codex CLI |
| Cursor rules | `.cursor/rules/*.mdc` | Cursor IDE |
| Gemini context | `GEMINI.md` | Google Gemini CLI |

## How to Run

```bash
# Dry-run (see what would change)
python3 scripts/generate_adapters.py

# Apply all adapters
python3 scripts/generate_adapters.py --apply

# Apply specific tools only
python3 scripts/generate_adapters.py --apply --tools kiro,codex

# Via CLI
python3 scripts/eeik_cli.py generate-adapters --apply
```

## Source of Truth

All adapters are generated from:
1. `project-manifest.yaml` — project name, technology stack, governance profile
2. `capability-packs/core/standards/golden-rules.md` — the 12 non-negotiable rules
3. `capability-packs/core/standards/security-baseline.md` — security requirements
4. Hard-coded architecture patterns (hexagonal + DDD) — these are non-negotiable

## Regeneration Triggers

Re-run this generator when:
- `project-manifest.yaml` changes
- Golden rules or standards are updated
- A new capability pack is added

The GitHub Actions workflow `.github/workflows/eeik-adapt.yml` does this automatically on manifest changes.

## Adapter Philosophy

Every adapter speaks the tool's native language but carries the same intelligence:

- **Kiro**: Three steering docs (product / tech / structure) — injected into every Kiro interaction
- **Codex**: Single `AGENTS.md` — Codex reads at repo root and in subdirectories
- **Cursor**: `.mdc` rule files with glob patterns — Cursor applies them per file type
- **Gemini**: Single `GEMINI.md` — equivalent to CLAUDE.md for Gemini CLI

All adapters reference `capability-packs/` and `knowledge/` for depth.
The adapters are entry points, not copies — keeping intelligence in one place.
