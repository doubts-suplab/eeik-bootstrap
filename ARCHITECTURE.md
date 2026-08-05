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
│   ▸ the dual role is now explicit: bootstrap/seed-manifest.yaml classifies every root
│     entry as seed | generated | engine; `eeik seed` copies exactly the seed set (ADR-011)
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

## Resolved rough edges

Per ADR-005, the taxonomy is documented *before* relocating content. Both Tier-4 rough edges are now
closed without moving content:

- **Dual-purpose adapters** — resolved (ADR-011). `bootstrap/seed-manifest.yaml` classifies every root
  entry as `seed` (copy) / `generated` (regenerate via the engine) / `engine` (never copy); `eeik seed`
  (also `eeik.seed_plan()`) copies exactly the `seed` set, and the seed's `quality-gate.yml` product
  jobs self-skip on the engine repo. A test asserts no engine-only path is ever classified `seed`.
- **Resolver overlap** — resolved. Unified on the single canonical
  `bootstrap/resolvers/capability-matrix.yaml`; the authoritative resolver is code
  (`eeik/packs.py::resolve_packs`); the duplicate `generators/capability-selector` stub was removed.
