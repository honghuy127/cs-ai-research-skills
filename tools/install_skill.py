#!/usr/bin/env python3
"""Install this checkout for supported coding agents without duplicating it."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_AGENTS = ("codex", "opencode", "claude")
NAME_PATTERN = re.compile(r"(?m)^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$")


@dataclass(frozen=True)
class InstallTarget:
    path: Path
    agents: tuple[str, ...]


def read_skill_name(source: Path) -> str:
    """Read and minimally validate the canonical name from SKILL.md."""
    skill_file = source / "SKILL.md"
    if not skill_file.is_file():
        raise ValueError(f"missing skill entrypoint: {skill_file}")
    text = skill_file.read_text(encoding="utf-8")
    match = NAME_PATTERN.search(text)
    if not match:
        raise ValueError(f"missing or invalid frontmatter name in {skill_file}")
    return match.group(1)


def install_targets(
    *,
    name: str,
    scope: str,
    agents: tuple[str, ...],
    home: Path,
    project_dir: Path | None,
) -> list[InstallTarget]:
    """Return the smallest set of discovery paths for the requested hosts."""
    selected = set(SUPPORTED_AGENTS if "all" in agents else agents)
    root = home if scope == "user" else project_dir
    if root is None:
        raise ValueError("--project-dir is required when --scope project is used")

    targets: list[InstallTarget] = []
    if scope == "user":
        if "codex" in selected or selected == set(SUPPORTED_AGENTS):
            consumers = ("codex", "opencode") if "opencode" in selected else ("codex",)
            targets.append(InstallTarget(root / ".agents" / "skills" / name, consumers))
        elif "opencode" in selected:
            targets.append(
                InstallTarget(root / ".config" / "opencode" / "skills" / name, ("opencode",))
            )
        if "claude" in selected:
            targets.append(InstallTarget(root / ".claude" / "skills" / name, ("claude",)))
    else:
        if "codex" in selected or selected == set(SUPPORTED_AGENTS):
            consumers = ("codex", "opencode") if "opencode" in selected else ("codex",)
            targets.append(InstallTarget(root / ".agents" / "skills" / name, consumers))
        elif "opencode" in selected:
            targets.append(InstallTarget(root / ".opencode" / "skills" / name, ("opencode",)))
        if "claude" in selected:
            targets.append(InstallTarget(root / ".claude" / "skills" / name, ("claude",)))

    return targets


def target_state(target: Path, source: Path) -> str:
    """Classify a destination without modifying it."""
    if target.is_symlink():
        return "installed" if target.resolve() == source else "conflict"
    if target.exists():
        return "installed" if target.resolve() == source else "conflict"
    return "missing"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Link this checkout into native skill discovery paths. The command is a dry run "
            "unless --apply is supplied, and it never replaces an existing destination."
        )
    )
    parser.add_argument("--scope", choices=("user", "project"), required=True)
    parser.add_argument(
        "--agents",
        choices=("all", *SUPPORTED_AGENTS),
        nargs="+",
        default=("all",),
        help="Hosts to configure; 'all' shares .agents/skills between Codex and OpenCode.",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Target repository; required for project scope.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Skill checkout to link (defaults to this repository).",
    )
    parser.add_argument("--apply", action="store_true", help="Create the planned links.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if "all" in args.agents and len(args.agents) > 1:
        print("error: --agents all cannot be combined with another agent", file=sys.stderr)
        return 2

    source = args.source.expanduser().resolve()
    project_dir = args.project_dir.expanduser().resolve() if args.project_dir else None
    if args.scope == "project" and project_dir is None:
        print("error: --project-dir is required when --scope project is used", file=sys.stderr)
        return 2
    if args.scope == "user" and project_dir is not None:
        print("error: --project-dir is only valid with --scope project", file=sys.stderr)
        return 2
    if project_dir == source:
        print("error: refusing to install a checkout inside itself", file=sys.stderr)
        return 2

    try:
        name = read_skill_name(source)
        targets = install_targets(
            name=name,
            scope=args.scope,
            agents=tuple(args.agents),
            home=Path.home(),
            project_dir=project_dir,
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    conflicts = [target for target in targets if target_state(target.path, source) == "conflict"]
    if conflicts:
        for target in conflicts:
            print(f"error: destination already exists: {target.path}", file=sys.stderr)
        print("No changes made. Remove or relocate conflicts explicitly, then retry.", file=sys.stderr)
        return 2

    changed = False
    for target in targets:
        hosts = ", ".join(target.agents)
        state = target_state(target.path, source)
        if state == "installed":
            print(f"ok [{hosts}]: {target.path} already points to {source}")
            continue
        if not args.apply:
            print(f"plan [{hosts}]: {target.path} -> {source}")
            continue
        target.path.parent.mkdir(parents=True, exist_ok=True)
        target.path.symlink_to(source, target_is_directory=True)
        changed = True
        print(f"linked [{hosts}]: {target.path} -> {source}")

    if not args.apply:
        print("Dry run only; pass --apply to create these links.")
    elif not changed:
        print("No changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
