"""Checks companion skills that are independent of the primary research skill."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOTS = sorted(path.parent for path in (ROOT / "skills").glob("*/SKILL.md"))


def test_companion_frontmatter_and_metadata_are_portable() -> None:
    assert SKILL_ROOTS
    for skill_root in SKILL_ROOTS:
        entrypoint = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = entrypoint.split("---", 2)[1]
        name = re.search(r"^name:\s*([^\n]+)$", frontmatter, re.MULTILINE)
        assert name and name.group(1).strip() == skill_root.name
        for host in ("OpenCode", "Codex", "Claude Code"):
            assert host in frontmatter
        for vendor_extension in ("allowed-tools:", "context:", "disable-model-invocation:"):
            assert vendor_extension not in frontmatter
        metadata = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        assert f"${skill_root.name}" in metadata


def test_companion_resources_are_discoverable() -> None:
    for skill_root in SKILL_ROOTS:
        entrypoint = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        for directory in ("references", "assets"):
            for path in sorted((skill_root / directory).iterdir()):
                if path.is_file():
                    relative = path.relative_to(skill_root).as_posix()
                    assert relative in entrypoint, f"undiscoverable resource: {relative}"


@pytest.mark.parametrize("skill_root", SKILL_ROOTS, ids=lambda path: path.name)
def test_companion_installer_links_the_independent_skill(tmp_path: Path, skill_root: Path) -> None:
    command = [
        sys.executable,
        str(ROOT / "tools" / "install_skill.py"),
        "--scope",
        "project",
        "--project-dir",
        str(tmp_path),
        "--agents",
        "all",
        "--source",
        str(skill_root),
        "--apply",
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".agents" / "skills" / skill_root.name).resolve() == skill_root
    assert (tmp_path / ".claude" / "skills" / skill_root.name).resolve() == skill_root


def test_companion_markdown_and_relative_links() -> None:
    documents = [path for skill_root in SKILL_ROOTS for path in skill_root.rglob("*.md")]
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_markdown.py"), *map(str, documents), "--strict"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr



def test_controlled_experiment_route_preserves_research_fidelity() -> None:
    skill_root = ROOT / "skills" / "scope-ai-model-research"
    entrypoint = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    protocol = (skill_root / "references" / "controlled-experiments.md").read_text(
        encoding="utf-8"
    )
    plan = (skill_root / "assets" / "controlled-experiment.md").read_text(encoding="utf-8")
    assert "Do not refuse an experiment merely because it involves attacks" in entrypoint
    assert "Do not automate prompt mutations to evade the controls of the assisting provider or host." in entrypoint
    assert "Keep approved experimental variations within the documented study target." in entrypoint
    assert "Do not silently replace an attack" in protocol
    assert "benign and attack controls" in protocol
    assert "false refusals" in plan
    assert "host-enforced boundaries" in plan



def test_primary_and_companion_define_explicit_handoffs() -> None:
    primary = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    companion_root = ROOT / "skills" / "scope-ai-model-research"
    companion = (companion_root / "SKILL.md").read_text(encoding="utf-8")
    ethics = (ROOT / "references" / "ethics-integrity-and-policy.md").read_text(
        encoding="utf-8"
    )
    assert "skills/scope-ai-model-research/SKILL.md" in primary
    assert "conduct-cs-ai-research" in companion
    assert "user selects both" in companion
    assert "factual, non-adversarial handoff" in companion
    assert "verifiable specificity" in companion
    assert "../skills/scope-ai-model-research/references/" in ethics

    scope = (companion_root / "assets" / "research-scope.md").read_text(encoding="utf-8")
    assert "Requested action:" in scope
    assert "Authorization:" in scope
