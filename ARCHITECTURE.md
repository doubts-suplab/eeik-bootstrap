# EEIK Architecture — directory taxonomy

> Where things live, and where new things go. This is the map referenced by
> [ADR-005](docs/decisions/ADR-005-layered-directory-taxonomy.md). Read it before adding a top-level
> directory or deciding where a file belongs.

EEIK is a **governed generation engine**, not a runnable product (that's APEX). Its repository is
organised into **four layers** with distinct lifecycles.

```
eeik-bootstrap/
├── ENGINE  ── executable Python; the only layer that runs ─────────────────────
│   ├── eeik/                 installable package (pip install -e . → `eeik` / python -m eeik)
│   │   ├── cli.py            command dispatch
│   │   ├── manifest.py       validate (canonical schema + governance rules)
│   │   ├── packs.py          manifest → .claude/ materialisation
│   │   ├── adapters.py       generate the 6 AI-tool adapters
│   │   ├── runner.py         run generators (via claude), --governed
│   │   ├── generation.py     HALO-governed generation seam (gate + audit + review)
│   │   ├── versions.py       pack versions + content digests
│   │   ├── lock.py           eeik.lock lockfile + drift detection
│   │   ├── catalog.py        queryable pack/agent/standard index
│   │   └── schemas/          THE canonical manifest schema (engine enforces it)
│   ├── scripts/              backward-compatible shims → the eeik package
│   ├── tests/                engine test suite
│   └── pyproject.toml        packaging + `eeik` console entry point
│
├── CONTENT  ── data the engine reads; Markdown/YAML, no code ──────────────────
│   ├── capability-packs/     19 versioned packs (agents, standards, knowledge, metadata.yaml)
│   ├── knowledge/            cross-project ADRs, patterns, lessons, reference architectures
│   ├── templates/            code + PROJECT-CLAUDE.md templates
│   ├── generators/           generator prompts, blueprints, workflows (the engine runs these)
│   └── bootstrap/            manifests, questions, resolvers, validators, examples
│
├── ADAPTERS  ── per-tool config: EEIK's own dogfood AND the copy seed ─────────
│   ├── .claude/  .github/  .kiro/  .cursor/          agent/instruction projections
│   ├── AGENTS.md  GEMINI.md                          root tool contexts
│   └── .vscode/  intellij/                           IDE settings
│
└── DOCS & META  ── human-facing ──────────────────────────────────────────────
    ├── docs/                 guide (index.html), decisions/ (ADRs), reference/, progress.md
    ├── README.md  ROADMAP.md  ARCHITECTURE.md  CLAUDE.md
    └── CONTRIBUTING.md  SECURITY.md  LICENSE
```

## Placement rule — "where does a new X go?"

| You are adding… | It goes in… |
|---|---|
| Python that *does* something | `eeik/` (a new module), with a `tests/` test |
| A capability pack, agent, standard, or knowledge asset | `capability-packs/<pack>/…` (with `metadata.yaml`, a `version`) |
| A generator prompt / blueprint / workflow | `generators/<generator>/…` |
| A manifest schema, question set, or resolver | `bootstrap/…` (the schema itself is canonical in `eeik/schemas/`) |
| A per-tool projection of existing content | the matching Adapter directory |
| Prose / an ADR / a reference doc | `docs/…` |

**Invariants**
- The engine (`eeik/`) reads content; content never imports the engine.
- There is exactly **one** canonical manifest schema: `eeik/schemas/manifest.schema.json`.
- Every capability pack declares a `version` in `metadata.yaml` (see ADR-004).
- Generation runs on HALO and is SUGGEST authority — drafts are staged, never auto-applied (ADR-003).

## Known rough edges (tracked, not yet moved)

Per ADR-005, the taxonomy is documented *before* relocating content. Outstanding in ROADMAP Tier 4:

- **Dual-purpose adapters** — the root `.claude/`/`.github/`/`.kiro/`/`.cursor/` are both EEIK's own
  config and the seed adopters copy. Make the copy-target explicit without breaking `cp -r`.
- **Resolver overlap** — `generators/capability-selector` vs `bootstrap/resolvers` overlap; unify.
