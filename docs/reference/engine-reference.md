# EEIK Engine Reference

The `eeik` engine exposes **one implementation over three surfaces** — CLI, Python SDK, and MCP.
This page is the surface-level reference: every command, function, and tool, plus what works offline and
how to run the MCP server in production.

> New to EEIK? Start with the [README Quick Start](../../README.md#quick-start) and run `eeik doctor`.

---

## CLI commands

| Command | What it does | Common flags |
|---|---|---|
| `eeik status` | Manifest, active packs, adapters | `--json` |
| `eeik validate [path]` | Validate a manifest (schema + governance) | `--strict` · `--json` |
| `eeik activate` | Materialise resolved packs into `.claude/` | `--apply` · `--clean` · `--list` |
| `eeik generate-adapters` | Generate the multi-tool adapters | `--apply` · `--tools …` |
| `eeik catalog` | Query the pack/agent/standard index | `--tag` · `--query` · `--provides` · `--json` |
| `eeik architectures [name]` | List/show reference architectures | `--json` |
| `eeik lock` / `diff` / `upgrade` | Pin / drift-check / re-pin `eeik.lock` | `diff --exit-code` · `--json` |
| `eeik verify` | Conformance gate — declared items exist | `--strict` · `--exit-code` · `--json` |
| `eeik lint` | Content quality — agents/standards well-formed | `--strict` · `--exit-code` · `--json` · `--show-pass` |
| `eeik doctor` | Diagnose adoption/health with a fix per issue | `--strict` · `--exit-code` · `--json` |
| `eeik contract` | Emit a HALO Agent Contract from a blueprint | `--blueprint` · `--name` · `--param` · `--validate` |
| `eeik seed` | Copy the seed set into a project | `--into DIR` · `--apply` · `--list` |
| `eeik lessons` | Closed-loop capture: audit → staged lessons | `--from FILE` · `--list` · `--json` |
| `eeik run <gen>` | Run a generator on the HALO harness | `--governed` · `--dry-run` |
| `eeik demo` | Offline governed-generation showcase | `--preview` |
| `eeik mcp` | Serve the read model over MCP | — |

`--exit-code` on `verify` / `diff` / `doctor` / `lint` makes them CI gates (non-zero on failure;
`--strict` also fails on warnings).

---

## Python SDK (`import eeik`)

The stable, typed in-process surface (ADR-007). Every result is a frozen dataclass with `.to_dict()`.

| Function | Returns |
|---|---|
| `find_packs(tag=…, query=…)` · `providers_of(name)` | `list[Pack]` · `list[Provider]` |
| `validate_manifest(path=/content=/manifest=)` | `ValidationResult` |
| `resolve_packs(…)` | `list[str]` |
| `pack_drift(lockfile=…)` · `write_lock(…)` | `DriftReport` · `Path` |
| `verify()` · `lint()` · `doctor()` | `VerifyReport` · `LintReport` · `DoctorReport` |
| `agent_contract(blueprint, name, **params)` · `validate_agent_contract(c)` | `dict` · `(ok, msg)` |
| `generate(generator, spec=…, preview=…)` | `GenerationOutcome` |
| `capture_lessons(records)` · `curated_lessons()` | `LessonCaptureReport` · `list[dict]` |
| `reference_architectures()` · `reference_architecture(name)` | `list[ReferenceArchitecture]` · `…` |
| `seed_plan()` | `dict` (seed / generated / engine) |

```python
import eeik
eeik.doctor().to_dict()                                # health, JSON-shaped
eeik.generate("agent-generator", spec="…", preview=True)   # governed, not persisted
```

---

## MCP server (`eeik mcp`)

Serves the read model over the Model Context Protocol (ADR-006). Tools:

**Read-only:** `eeik_catalog` · `eeik_validate_manifest` · `eeik_resolve_packs` · `eeik_pack_drift` ·
`eeik_verify` · `eeik_lint` · `eeik_reference_architectures` · `eeik_doctor`

**Governed writes** (SUGGEST authority — staged for human review, never auto-applied):
`eeik_generate` (supports `preview`) · `eeik_capture_lessons`

### Host configuration

Claude Code (`.mcp.json`) or any stdio MCP host:

```json
{ "mcpServers": { "eeik": { "command": "eeik", "args": ["mcp"] } } }
```

If installed in a virtualenv, point `command` at that venv's `eeik` (or use
`{"command": "python", "args": ["-m", "eeik", "mcp"]}`).

### Running MCP in production

The engine intentionally ships **no** auth or rate-limiting — it is a local stdio server by design, and
a governed write only ever *stages* a draft (an MCP host cannot make the engine mutate live config).
When exposing it beyond a single user's machine, put the controls at the **host / transport**, not the
engine:

- **Transport & auth.** Run it behind an MCP gateway that terminates auth (mTLS / OAuth) — don't expose
  the stdio process directly to untrusted callers.
- **Rate-limiting.** Apply per-principal limits at the gateway; the read tools are cheap, but
  `eeik_generate` / `eeik_capture_lessons` do real work and write to `.eeik-staging/`.
- **Filesystem isolation.** The engine writes only to `.claude/` and `.eeik-staging/` under its working
  directory — run it in a workspace scoped to the project it serves.
- **Least privilege.** If a host only needs answers, it never needs the write tools; expose the
  read-only subset.

See [SECURITY.md → Engine Security Model](../../SECURITY.md#engine-security-model) for the full contract.

---

## What works offline (with / without HALO)

HALO (`agent-harness`) is an **optional** dependency. `eeik doctor` reports exactly what's available in
your environment.

| Capability | No HALO installed | With HALO |
|---|---|---|
| `validate` · `resolve` · `catalog` · `verify` · `lint` · `diff` · `doctor` · `seed` · `contract` · `architectures` | ✅ works | ✅ works |
| `eeik demo` / `generate` / `capture_lessons` | ✅ runs **fail-safe** — draft staged (or previewed) but **ungoverned**, with a warning | ✅ fully **governed** — confidence gate, audit, human-review routing |
| `auto_enforced` on any generation | always `False` | always `False` |

Nothing requires network access: the engine's runtime deps are `pyyaml` + `jsonschema` only. An
LLM-backed generation path exists but needs the `claude` CLI / an API key you supply — absent that,
generation uses a deterministic offline producer.
