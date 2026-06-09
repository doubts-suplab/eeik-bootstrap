# Codex Subdirectory AGENTS.md Templates

Codex CLI reads `AGENTS.md` files recursively — not just the root one. Each subdirectory
`AGENTS.md` provides directory-specific context, overriding or extending the root file.

This is the **most powerful Codex pattern**: targeted intelligence exactly where the code lives.

## Deployment Map

| Template file | Deploy to (in your project) |
|---|---|
| `src-main-java-AGENTS.md` | `src/main/java/AGENTS.md` |
| `src-test-AGENTS.md` | `src/test/AGENTS.md` |
| `infrastructure-AGENTS.md` | `infrastructure/AGENTS.md` |
| `python-AGENTS.md` | `python/AGENTS.md` or root of Python project |
| `data-pipelines-AGENTS.md` | `data-pipelines/AGENTS.md` or `pipelines/AGENTS.md` |

## How to Deploy

```bash
# Java Spring Boot project
cp generators/adapter-generator/codex-subdirs/src-main-java-AGENTS.md  src/main/java/AGENTS.md
cp generators/adapter-generator/codex-subdirs/src-test-AGENTS.md        src/test/AGENTS.md
cp generators/adapter-generator/codex-subdirs/infrastructure-AGENTS.md  infrastructure/AGENTS.md

# Python project
cp generators/adapter-generator/codex-subdirs/python-AGENTS.md          src/AGENTS.md

# Data pipeline project
cp generators/adapter-generator/codex-subdirs/data-pipelines-AGENTS.md  pipelines/AGENTS.md
```

Or run the adapter generator which will do this automatically:
```bash
python3 scripts/generate_adapters.py --apply --tools codex
```

## Why This Matters

The root `AGENTS.md` is general context. Subdirectory files are **laser-focused**:

- `src/main/java/AGENTS.md` → Codex knows it's in hexagonal architecture, Spring Boot 3, `jakarta.*`
- `src/test/AGENTS.md` → Codex knows to use Testcontainers, Awaitility, AssertJ
- `infrastructure/AGENTS.md` → Codex knows CDK L2/L3 constructs, encryption defaults, no `*` IAM

Without these, Codex applies root context everywhere — you lose the layer-specific intelligence.
