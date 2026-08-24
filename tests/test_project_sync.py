"""Repository-level checks that keep the skill package connected."""

from __future__ import annotations

import re
from pathlib import Path

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
    resources = [
        *(ROOT / "scripts").glob("*.py"),
        *(ROOT / "assets").iterdir(),
    ]
    for path in sorted(resources):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        assert relative in instructions, f"undiscoverable skill resource: {relative}"
