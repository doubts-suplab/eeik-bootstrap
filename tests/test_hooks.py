"""Tests for the shell safety hooks (.claude/hooks/*.sh).

The hooks are the runtime guard rails: pre-bash-guard blocks destructive commands, pre-write-guard
blocks writes to dangerous paths, and post-edit-check warns (never blocks) on anti-patterns. They read
a JSON payload on stdin and signal via exit code (2 = block, 0 = allow). Previously untested shell —
these subprocess tests pin the block/allow contract.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1] / ".claude" / "hooks"

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")


def _run(script: str, payload: dict) -> tuple[int, str]:
    proc = subprocess.run(
        ["bash", str(HOOKS / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stderr


# ── pre-bash-guard: destructive commands are blocked (exit 2) ───────────────────

@pytest.mark.parametrize("command", [
    "git push --force origin feature",
    "git push -f origin feature",
    "git reset --hard HEAD~3",
    "rm -rf /",
    "rm -rf /home",
    "psql -c 'DROP DATABASE prod'",
    "cdk destroy",
    "aws ec2 terminate-instances --instance-ids i-123",
])
def test_pre_bash_guard_blocks_destructive(command):
    rc, err = _run("pre-bash-guard.sh", {"command": command})
    assert rc == 2, f"expected block for: {command}"
    assert "BLOCKED" in err or "blocked" in err.lower()


@pytest.mark.parametrize("command", [
    "git push origin main",      # protected branch — warn, don't block
    "git clean -fd",             # deletes untracked — warn, don't block
])
def test_pre_bash_guard_warns_but_allows(command):
    rc, err = _run("pre-bash-guard.sh", {"command": command})
    assert rc == 0               # a warning, not a hard block
    assert "WARNING" in err


@pytest.mark.parametrize("command", [
    "ls -la",
    "git status",
    "git push origin feature/my-branch",
    "pytest tests/ -q",
    "rm -rf ./build",
])
def test_pre_bash_guard_allows_safe(command):
    rc, _ = _run("pre-bash-guard.sh", {"command": command})
    assert rc == 0, f"expected allow for: {command}"


def test_pre_bash_guard_allows_empty_command():
    rc, _ = _run("pre-bash-guard.sh", {})
    assert rc == 0


# ── pre-write-guard: dangerous paths are blocked ────────────────────────────────

@pytest.mark.parametrize("path", [
    "/etc/passwd",
    "/usr/bin/thing",
    "secrets/server.key",
    "certs/cert.pem",
    "config/keystore.p12",
    ".env.production",
    "app/.env.prod",
])
def test_pre_write_guard_blocks_dangerous_paths(path):
    rc, err = _run("pre-write-guard.sh", {"file_path": path})
    assert rc == 2, f"expected block for: {path}"
    assert "BLOCKED" in err


@pytest.mark.parametrize("path", [
    "src/main/java/App.java",
    "eeik/doctor.py",
    "docs/index.html",
    "README.md",
])
def test_pre_write_guard_allows_normal_paths(path):
    rc, _ = _run("pre-write-guard.sh", {"file_path": path})
    assert rc == 0, f"expected allow for: {path}"


# ── post-edit-check: warns but never blocks (always exit 0) ─────────────────────

def test_post_edit_check_warns_but_never_blocks(tmp_path: Path):
    java = tmp_path / "Bad.java"
    java.write_text("class Bad { void f(){ System.out.println(\"x\"); } }\n")
    rc, err = _run("post-edit-check.sh", {"file_path": str(java)})
    assert rc == 0                        # never blocks
    assert "System.out" in err or "SLF4J" in err   # but it warned


def test_post_edit_check_clean_file_is_silent_and_allows(tmp_path: Path):
    py = tmp_path / "ok.py"
    py.write_text("import logging\nlog = logging.getLogger(__name__)\nlog.info('hi')\n")
    rc, _ = _run("post-edit-check.sh", {"file_path": str(py)})
    assert rc == 0


def test_post_edit_check_missing_file_is_noop():
    rc, _ = _run("post-edit-check.sh", {"file_path": "/nonexistent/path/file.java"})
    assert rc == 0
