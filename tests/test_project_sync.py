"""Repository-level checks that keep the skill package connected."""

from __future__ import annotations

import importlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"


def skill_name() -> str:
    text = SKILL.read_text(encoding="utf-8")
    match = re.search(r"\A---\n.*?^name:\s*([^\n]+)$.*?\n---\n", text, re.MULTILINE | re.DOTALL)
    assert match, "SKILL.md must contain a frontmatter name"
    return match.group(1).strip()


def test_interface_metadata_invokes_the_installed_skill() -> None:
    metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert f"${skill_name()}" in metadata


def test_portable_frontmatter_declares_supported_hosts() -> None:
    entrypoint = SKILL.read_text(encoding="utf-8")
    frontmatter = entrypoint.split("---", 2)[1]
    for host in ("OpenCode", "Codex", "Claude Code"):
        assert host in frontmatter
    for vendor_extension in ("allowed-tools:", "context:", "disable-model-invocation:"):
        assert vendor_extension not in frontmatter


def test_installer_uses_one_shared_checkout_for_all_agents(tmp_path: Path) -> None:
    installer = ROOT / "tools" / "install_skill.py"
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    env = {"HOME": str(home)}

    command = [
        sys.executable,
        str(installer),
        "--scope",
        "project",
        "--project-dir",
        str(project),
        "--agents",
        "all",
        "--apply",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    shared = project / ".agents" / "skills" / skill_name()
    claude = project / ".claude" / "skills" / skill_name()
    assert shared.is_symlink() and shared.resolve() == ROOT
    assert claude.is_symlink() and claude.resolve() == ROOT
    assert not (project / ".opencode" / "skills" / skill_name()).exists()

    repeated = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert repeated.returncode == 0, repeated.stderr
    assert "No changes needed." in repeated.stdout


def test_installer_is_dry_run_first_and_refuses_conflicts(tmp_path: Path) -> None:
    installer = ROOT / "tools" / "install_skill.py"
    project = tmp_path / "project"
    conflict = project / ".opencode" / "skills" / skill_name()
    conflict.mkdir(parents=True)

    dry_run = subprocess.run(
        [
            sys.executable,
            str(installer),
            "--scope",
            "project",
            "--project-dir",
            str(project),
            "--agents",
            "claude",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert dry_run.returncode == 0
    assert not (project / ".claude").exists()

    conflict_result = subprocess.run(
        [
            sys.executable,
            str(installer),
            "--scope",
            "project",
            "--project-dir",
            str(project),
            "--agents",
            "opencode",
            "--apply",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert conflict_result.returncode == 2
    assert "destination already exists" in conflict_result.stderr


def test_all_references_are_routed_from_the_entrypoint() -> None:
    entrypoint = SKILL.read_text(encoding="utf-8")
    for path in sorted((ROOT / "references").glob("*.md")):
        relative = path.relative_to(ROOT).as_posix()
        assert relative in entrypoint, f"unrouted reference: {relative}"


def test_all_helpers_and_assets_are_discoverable_from_instructions() -> None:
    instruction_files = [SKILL, *(ROOT / "references").glob("*.md")]
    instructions = "\n".join(path.read_text(encoding="utf-8") for path in instruction_files)
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    for path in scripts:
        relative = path.relative_to(ROOT).as_posix()
        if path.read_bytes().startswith(b"#!"):
            assert relative in instructions, f"undiscoverable executable helper: {relative}"
        else:
            consumers = "\n".join(
                candidate.read_text(encoding="utf-8") for candidate in scripts if candidate != path
            )
            assert path.stem in consumers, f"unreferenced internal helper: {relative}"

    for path in sorted((ROOT / "assets").iterdir()):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        assert relative in instructions, f"undiscoverable skill resource: {relative}"


def test_executables_share_one_runtime_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    contract = importlib.import_module("research_contract")
    audit = importlib.import_module("audit_research")
    capture = importlib.import_module("capture_run")
    markdown = importlib.import_module("check_markdown")
    office = importlib.import_module("check_office")
    state = importlib.import_module("research_state")
    drawio = importlib.import_module("validate_drawio")

    assert state.VALID_STATUSES is contract.VALID_STATUSES
    assert audit.EMPIRICAL_TYPES is contract.EMPIRICAL_TYPES
    assert capture.MAX_HASH_BYTES is contract.MAX_HASH_BYTES
    assert markdown.PLACEHOLDERS is contract.PLACEHOLDERS
    assert office.PLACEHOLDERS is contract.PLACEHOLDERS
    assert drawio.PLACEHOLDERS is contract.PLACEHOLDERS
