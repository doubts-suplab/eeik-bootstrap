# ADR-004 — Capability packs are versioned; `eeik.lock` records what a repo adopted

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — making adoption reproducible and upgradeable

---

## Context and Problem Statement

EEIK's adoption model is **copy-once**: a project runs `cp -r .claude` (or `activate_packs.py`) and
the pack files are materialised into the target repo. From that moment the target **silently forks**
from the source. There is no record of *which version* of a pack was adopted, and no way to learn
that the upstream pack has since improved. Engineering standards adopted this way **rot**: the whole
premise of EEIK — "capture engineering intelligence once, reuse it everywhere" — is undermined if
adopters can never receive updates.

---

## Decision

**Treat capability packs like versioned dependencies.**

- Every pack declares a `version` in its `metadata.yaml` (packs that lacked one now have it).
- `eeik lock` writes **`eeik.lock`** — a reproducible record of every adopted pack's `version` and a
  16-char content **digest** (SHA-256 over the pack's materialised Markdown surface).
- `eeik diff` compares `eeik.lock` against the current packs and reports **drift**, classified as:
  `added`, `removed`, `version-changed`, or `content-changed` (an upstream edit with no version bump).
  `--exit-code` makes it a **CI gate** (exits `2` when drift exists).
- `eeik upgrade` re-pins `eeik.lock` to current versions and points the user at `activate --clean` to
  re-materialise.

The digest matters because it catches the common failure mode the version field alone misses: a
maintainer edits a standard without bumping `version`. The digest still changes, so `eeik diff`
flags it.

---

## Considered Options

1. **Versions + lockfile + content digest (chosen)** — reproducible, detects both declared and silent
   drift, CI-enforceable. The "package manager for engineering intelligence" model.
2. **Version field only, no lockfile** — rejected: no per-repo record of what was adopted; misses
   un-versioned content edits.
3. **Git submodules for packs** — rejected: heavyweight for adopters, poor fit for the "drop files in"
   ergonomics EEIK is valued for, and couples every repo to EEIK's git history.

---

## Consequences

**Positive**
- Adoption is reproducible; `eeik.lock` is the manifest of *what engineering intelligence a repo runs*.
- Drift is visible and CI-gateable, turning "scaffold once, rot forever" into "living standards".
- Prerequisite for a future `eeik upgrade --apply` that safely merges upstream pack improvements.

**Negative / trade-offs**
- One more file (`eeik.lock`) in adopting repos, and a habit (`lock` after `activate`) to learn.
- Digest is over the Markdown surface only (agents/commands/standards/workflows); non-Markdown assets
  are out of scope for v1 of the digest.

---

## Related

- ADR-003 — EEIK generators run on HALO.
- `scripts/pack_versions.py`, `scripts/eeik_lock.py`, `tests/test_engine.py`.
