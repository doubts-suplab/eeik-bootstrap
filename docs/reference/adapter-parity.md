# Adapter Parity Matrix

EEIK projects the same intelligence into **six** AI coding tools. The tools differ in what their config
formats can express, so depth is not identical — this matrix makes the gap explicit, so adopters know
what to expect per tool and contributors know where to invest.

## Current depth (this repo)

| Tool | Directory | Agents | Standards / Instructions | Commands / Prompts | Hooks | Depth |
|---|---|---:|---:|---:|---:|---|
| **Claude Code** | `.claude/` | 50 | 27 standards | 28 commands | 4 | 🟢 Full |
| **GitHub Copilot** | `.github/` | 48 | 35 instructions | 36 prompts | — | 🟢 Full |
| **Cursor** | `.cursor/rules/` | — | 4 `.mdc` rules (glob-scoped) | — | — | 🟡 Rules |
| **Kiro** | `.kiro/` | — | steering docs | — | hooks + settings | 🟡 Steering |
| **Codex CLI** | `AGENTS.md` (+ per-dir) | context file | embedded | — | — | 🟡 Context |
| **Gemini CLI** | `GEMINI.md` | context file | embedded | — | — | 🟡 Context |

🟢 **Full** — agents + standards + commands (+ hooks) as first-class, individually-addressable files.
🟡 **Rules / Steering / Context** — the tool's format expresses standards + project context, but not the
full agent/command catalogue; guidance is consolidated into fewer files.

## Why the gap

The depth follows what each tool's configuration model natively supports:

- **Claude Code** and **Copilot** support many discrete agent/instruction/prompt files selected by
  description or file glob — so the full pack catalogue projects cleanly.
- **Cursor** applies `.mdc` rules by glob; **Kiro** uses always-on steering docs; **Codex** and
  **Gemini** read a single persistent context file. These are excellent for *standards and project
  context* but are not designed to host 50 individually-triggered agents.

This is a tool-capability difference, not a content gap — the *same* standards and golden rules reach
every tool; only the granularity of agent/command addressing differs.

## The parity goal

The multi-tool adapter generator (`eeik generate-adapters`) is the single source that projects EEIK's
content into each format. The goal for the thinner adapters is **coverage parity of standards and
context** (every tool enforces the same rules), while accepting **format-appropriate granularity** for
agents/commands. Concretely:

- **Keep standards + golden rules at parity across all six** — this is the non-negotiable floor.
- For Cursor/Kiro/Codex/Gemini, **consolidate the most-used agents' guidance** into the tool's
  rules/steering/context rather than attempting 1:1 agent files the format can't trigger.
- Track new tools as they appear via the same generator (see ROADMAP §8, "Broader tool support").

## For contributors

When you add or change a standard, run `eeik generate-adapters --apply` so every tool's projection stays
in sync — don't hand-edit one adapter in isolation. `eeik lint` checks agent/standard well-formedness;
`eeik verify` checks the pack declares what it ships.
