"""Repository-level checks that keep the skill package connected."""

from __future__ import annotations

import importlib
import re
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
