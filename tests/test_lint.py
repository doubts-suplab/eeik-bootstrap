"""Tests for `eeik lint` — content-quality checks for agents + standards."""

from __future__ import annotations

import importlib
from pathlib import Path

import eeik
from eeik import mcp_tools

lint_mod = importlib.import_module("eeik.lint")

_GOOD_DESC = "x" * 60


def _agent(tmp_path: Path, body: str, name: str = "foo.md") -> Path:
    f = tmp_path / name
    f.write_text(body)
    return f


def test_shipped_content_is_lint_clean():
    report = eeik.lint()
    assert isinstance(report, eeik.LintReport)
    # No malformed agent/standard content ships (fails would block the catalog's honesty).
    assert report.ok, [f.to_dict() for f in report.fails]


def test_missing_frontmatter_is_a_fail(tmp_path: Path):
    f = _agent(tmp_path, "# Just a heading\n\nbody")
    levels = {x.rule: x.level for x in lint_mod.lint_agent_file(f)}
    assert levels.get("frontmatter") == "fail"


def test_managed_marker_is_ignored(tmp_path: Path):
    # `eeik activate` prepends a marker to materialised copies; the linter must see the frontmatter.
    f = _agent(tmp_path, f"# eeik-managed pack=x\n---\nname: foo\ndescription: {_GOOD_DESC}\n"
                         f"model: m\n---\n# Foo\n")
    findings = lint_mod.lint_agent_file(f)
    assert [x.level for x in findings] == ["pass"]


def test_thin_description_and_missing_model_warn(tmp_path: Path):
    f = _agent(tmp_path, "---\nname: foo\ndescription: short\n---\n# Foo\n")
    rules = {x.rule: x.level for x in lint_mod.lint_agent_file(f)}
    assert rules["description-length"] == "warn"
    assert rules["model"] == "warn"


def test_name_must_match_filename(tmp_path: Path):
    f = _agent(tmp_path, f"---\nname: bar\ndescription: {_GOOD_DESC}\nmodel: m\n---\n# Bar\n", name="foo.md")
    rules = {x.rule: x.level for x in lint_mod.lint_agent_file(f)}
    assert rules.get("name-matches-file") == "warn"


def test_unknown_tool_warns(tmp_path: Path):
    f = _agent(tmp_path, f"---\nname: foo\ndescription: {_GOOD_DESC}\nmodel: m\n"
                         f"tools: [Read, Nope]\n---\n# Foo\n")
    assert any(x.rule == "tools" and x.level == "warn" for x in lint_mod.lint_agent_file(f))


def test_empty_standard_is_a_fail(tmp_path: Path):
    f = tmp_path / "std.md"
    f.write_text("   \n")
    assert lint_mod.lint_standard_file(f)[0].level == "fail"


def test_lint_never_crashes_on_out_of_tree_path(tmp_path: Path):
    # _rel must not raise for a path outside the repo root.
    f = _agent(tmp_path, "# no frontmatter")
    findings = lint_mod.lint_agent_file(f)
    assert findings and findings[0].file == "foo.md"


def test_mcp_lint_tool_registered():
    res = mcp_tools.dispatch("eeik_lint", {})
    assert set(res) >= {"ok", "counts", "findings"}
    assert "eeik_lint" in {t["name"] for t in mcp_tools.TOOLS}
