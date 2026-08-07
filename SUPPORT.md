# Support & FAQ

Need help adopting or running EEIK? Start here.

## Getting help

1. **Run the doctor.** `eeik doctor` diagnoses the most common problems (deps, HALO/MCP, manifest,
   pack resolution, adapters, lock drift, conformance) and prints an actionable fix for each.
2. **Read the guide.** `docs/index.html` is the visual overview; `README.md` has the Quick Start;
   `ARCHITECTURE.md` explains the layout.
3. **Search issues / open one.** File a GitHub issue with the `question` or `bug` label. Include the
   output of `eeik doctor --json` and `eeik --help`.
4. **Security issues** go through [SECURITY.md](SECURITY.md) — do **not** open a public issue.

## FAQ

**Is EEIK a runnable application?**
No. EEIK is a *bootstrap + governed generation engine*. It supplies configuration for six AI coding
tools and an installable `eeik` engine that validates manifests, resolves capability packs, and
governs generation. Products like APEX *consume* it.

**How do I adopt EEIK into my project?**
`eeik seed --into <dir> --apply` copies the seed set (adapter shells + shared config) into your
project — not the engine, not tests, not EEIK's own agents. Then write a `project-manifest.yaml` and run
`eeik activate --apply` to materialise the packs you selected. See the README Quick Start.

**What's the difference between the seed and the engine?**
The *seed* is the config you copy into a project (`.github/instructions`, editor settings, a starter
`CLAUDE.md`). The *engine* (`pip install eeik`) is the tool you run to validate, resolve, generate, and
verify. `bootstrap/seed-manifest.yaml` classifies every root entry as `seed` / `generated` / `engine`.

**Do I need HALO (`agent-harness`) installed?**
No — it's optional. Without it, governed generation runs *fail-safe* (drafts are staged, ungoverned)
and `eeik demo` runs offline. `eeik doctor` tells you exactly what works with and without it. Install
it (`pip install agent-harness`) for a certified confidence gate.

**Does generation ever change my files automatically?**
No. Generation is **SUGGEST authority** — every draft (agents, lessons) is written to `.eeik-staging/`
and staged for human review. A human curates and commits. It is never auto-applied.

**Which Python versions are supported?**
Python 3.11, 3.12, and 3.13 (tested in CI).

**How do I check my adoption is healthy / CI-gate it?**
`eeik doctor --strict --exit-code`, plus `eeik verify --strict --exit-code` and `eeik diff --exit-code`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations. A good first contribution is
improving one standard or adding one worked example.
