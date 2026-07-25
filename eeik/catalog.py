#!/usr/bin/env python3
"""
EEIK Catalog — a queryable index of capability packs, agents, commands, and standards.

Turns the ``capability-packs/`` folder from a directory you browse by hand into a machine-readable
registry you can query: *"which packs support banking + FHIR?"*, *"which pack provides the
`java-architect` agent?"*. This is the read model the planned EEIK MCP server exposes (ROADMAP Tier 2),
and it is pure-Python + offline — no LLM, no network.

    eeik catalog                      # human-readable table of every pack
    eeik catalog --tag banking        # packs tagged 'banking'
    eeik catalog --query fhir         # packs matching 'fhir' (name / description / tags)
    eeik catalog --provides java-architect   # which pack provides that agent/command/standard
    eeik catalog --json               # machine-readable index (stdout, or --output <path>)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eeik.versions import PACKS_DIR, normalise_version, pack_fingerprint, read_pack_metadata

REPO_ROOT = Path(__file__).parent.parent
CATALOG_SCHEMA_VERSION = 1

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"


def _as_list(value: object) -> list[str]:
    """Coerce a metadata field that may be a list, a scalar, or None into a list of strings."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v is not None]
    return [str(value)]


def _clean_description(raw: object) -> str:
    """Collapse a folded/multi-line YAML description into a single line."""
    return " ".join(str(raw or "").split())


def _category_of(meta: dict) -> str:
    """A pack's category, inferred when not declared (core packs often set `always_active` instead)."""
    if meta.get("category"):
        return str(meta["category"])
    if meta.get("always_active"):
        return "core"
    return "uncategorised"


def pack_entry(pack_dir: Path) -> dict:
    """Build one catalog entry for a pack directory."""
    meta = read_pack_metadata(pack_dir)
    fp = pack_fingerprint(pack_dir)
    return {
        "name": meta.get("name", pack_dir.name),
        "pack": pack_dir.name,
        "version": normalise_version(meta.get("version")),
        "category": _category_of(meta),
        "description": _clean_description(meta.get("description")),
        "tags": _as_list(meta.get("tags")),
        "agents": _as_list(meta.get("agents_provided")),
        "commands": _as_list(meta.get("commands_provided")),
        "standards": _as_list(meta.get("standards_provided")),
        "digest": fp["digest"],
    }


def build_catalog(packs: list[str] | None = None) -> dict:
    """Assemble the full catalog document (all packs on disk unless a subset is given)."""
    from datetime import datetime, timezone

    if packs is None:
        names = sorted(p.name for p in PACKS_DIR.iterdir() if p.is_dir())
    else:
        names = list(packs)
    entries = [pack_entry(PACKS_DIR / n) for n in names if (PACKS_DIR / n).is_dir()]
    return {
        "schemaVersion": CATALOG_SCHEMA_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "packCount": len(entries),
        "packs": entries,
    }


# ── queries ───────────────────────────────────────────────────────────────────

def filter_by_tag(entries: list[dict], tag: str) -> list[dict]:
    t = tag.lower()
    return [e for e in entries if t in [x.lower() for x in e["tags"]]]


def filter_by_query(entries: list[dict], query: str) -> list[dict]:
    """Match a free-text query against pack name, description, and tags."""
    q = query.lower()
    out = []
    for e in entries:
        hay = " ".join([e["name"], e["pack"], e["description"], " ".join(e["tags"])]).lower()
        if q in hay:
            out.append(e)
    return out


def find_providers(entries: list[dict], name: str) -> list[tuple[str, str]]:
    """Return (pack, kind) pairs for every pack that provides an agent/command/standard called `name`."""
    n = name.lower()
    hits: list[tuple[str, str]] = []
    for e in entries:
        for kind in ("agents", "commands", "standards"):
            if n in [x.lower() for x in e[kind]]:
                hits.append((e["pack"], kind[:-1]))  # singular: agent/command/standard
    return hits


# ── rendering ───────────────────────────────────────────────────────────────────

def print_table(entries: list[dict]) -> None:
    if not entries:
        print(f"  {ANSI_YELLOW}No packs match.{ANSI_RESET}")
        return
    print(f"  {ANSI_BOLD}{'PACK':<20} {'VER':<6} {'CATEGORY':<14} {'A/C/S':<9} TAGS{ANSI_RESET}")
    for e in entries:
        acs = f"{len(e['agents'])}/{len(e['commands'])}/{len(e['standards'])}"
        tags = ", ".join(e["tags"][:4])
        print(f"  {e['pack']:<20} {e['version']:<6} {e['category']:<14} {acs:<9} {ANSI_DIM}{tags}{ANSI_RESET}")
    print(f"\n  {ANSI_DIM}A/C/S = agents / commands / standards provided{ANSI_RESET}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK capability catalog (queryable pack index)")
    parser.add_argument("--tag", metavar="TAG", help="Only packs carrying this tag")
    parser.add_argument("--query", metavar="TEXT", help="Match name / description / tags")
    parser.add_argument("--provides", metavar="NAME",
                        help="Which pack provides this agent / command / standard")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--output", metavar="PATH", help="Write JSON to a file instead of stdout")
    args = parser.parse_args()

    catalog = build_catalog()
    entries = catalog["packs"]

    # --provides is a lookup, not a filter.
    if args.provides:
        hits = find_providers(entries, args.provides)
        if args.json:
            print(json.dumps({"name": args.provides, "providers": [
                {"pack": p, "kind": k} for p, k in hits]}, indent=2))
            return 0
        print(f"\n{ANSI_BOLD}Providers of '{args.provides}'{ANSI_RESET}")
        if not hits:
            print(f"  {ANSI_YELLOW}No pack provides '{args.provides}'.{ANSI_RESET}\n")
            return 1
        for pack, kind in hits:
            print(f"  {ANSI_GREEN}✓{ANSI_RESET} {pack}  {ANSI_DIM}({kind}){ANSI_RESET}")
        print()
        return 0

    if args.tag:
        entries = filter_by_tag(entries, args.tag)
    if args.query:
        entries = filter_by_query(entries, args.query)

    if args.json:
        doc = dict(catalog, packs=entries, packCount=len(entries))
        text = json.dumps(doc, indent=2)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
            print(f"{ANSI_GREEN}✓ Wrote {args.output} ({len(entries)} packs){ANSI_RESET}")
        else:
            print(text)
        return 0

    print(f"\n{ANSI_BOLD}EEIK Capability Catalog{ANSI_RESET}  "
          f"{ANSI_DIM}({len(entries)} of {catalog['packCount']} packs){ANSI_RESET}\n")
    print_table(entries)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
