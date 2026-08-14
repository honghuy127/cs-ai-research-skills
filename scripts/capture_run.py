#!/usr/bin/env python3
"""Create an immutable provenance manifest for a research run.

The script records a run; it never executes the supplied command. A completed
full measured run remains only candidate evidence until its outputs and analysis
are independently checked.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from research_state import validate as validate_dossier  # noqa: E402

MAX_HASH_BYTES = 64 * 1024 * 1024
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
EXPERIMENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_timestamp(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a UTC offset or Z")
    return parsed


def resolve_file(raw_path: str, root: Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(raw_path: str, root: Path, external_version: str | None = None) -> dict:
    path = resolve_file(raw_path, root)
    record = {"path": str(path), "exists": path.is_file()}
    if not path.is_file():
        return record
    stat = path.stat()
    record.update({"size_bytes": stat.st_size, "modified_at_ns": stat.st_mtime_ns})
    if external_version:
        record["external_version"] = external_version
    if stat.st_size > MAX_HASH_BYTES:
        record.update(
            {"sha256": None, "hash_note": "skipped: file exceeds 64 MiB; immutable external version recorded"}
        )
        return record
    record["sha256"] = hash_file(path)
    return record


def parse_versions(values: list[str], root: Path) -> tuple[dict[str, str], str | None]:
    versions: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            return {}, f"invalid --file-version {value!r}; expected PATH=IMMUTABLE_ID"
        raw_path, version = value.rsplit("=", 1)
        if not raw_path.strip() or not version.strip():
            return {}, f"invalid --file-version {value!r}; path and immutable ID must be non-empty"
        key = str(resolve_file(raw_path, root))
        if key in versions and versions[key] != version.strip():
            return {}, f"conflicting immutable IDs for {key}"
        versions[key] = version.strip()
    return versions, None


def git_record(root: Path) -> dict:
    def run(*parts: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            ["git", *parts],
            cwd=root,
            capture_output=True,
            check=False,
        )

    commit = run("rev-parse", "HEAD")
    if commit.returncode != 0:
        return {"available": False}
    status = run("status", "--porcelain=v1")
    branch = run("branch", "--show-current")
    tracked = run("diff", "--name-only", "-z", "HEAD")
    untracked = run("ls-files", "--others", "--exclude-standard", "-z")

    dirty_paths: set[str] = set()
    for result in (tracked, untracked):
        if result.returncode == 0:
            for raw in result.stdout.split(b"\0"):
                if raw:
                    dirty_paths.add(os.fsdecode(raw))

    dirty_files: list[dict] = []
    for relative in sorted(dirty_paths):
        normalized = relative.replace("\\", "/")
        if normalized == ".research" or normalized.startswith(".research/"):
            continue
        path = root / relative
        record: dict = {"path": normalized}
        if path.is_symlink():
            record.update({"kind": "symlink", "target": os.readlink(path)})
        elif path.is_file():
            size = path.stat().st_size
            record.update({"kind": "file", "size_bytes": size})
            if size <= MAX_HASH_BYTES:
                record["sha256"] = hash_file(path)
            else:
                record.update(
                    {
                        "sha256": None,
                        "hash_note": "dirty file exceeds 64 MiB; preserve a separate source or data snapshot",
                    }
                )
        else:
            record["kind"] = "deleted-or-unavailable"
        dirty_files.append(record)

    return {
        "available": True,
        "commit": commit.stdout.decode("ascii", errors="replace").strip(),
        "branch": branch.stdout.decode(errors="replace").strip() or None,
        "dirty": bool(status.stdout.strip()),
        "status_porcelain": status.stdout.decode(errors="replace").splitlines(),
        "dirty_file_hashes": dirty_files,
        "dirty_snapshot_scope": "tracked changes and untracked non-ignored files, excluding .research runtime state",
        "dirty_snapshot_complete": tracked.returncode == 0 and untracked.returncode == 0,
    }


def parse_existing_run_ids(path: Path) -> set[str]:
    values: set[str] = set()
    if not path.exists():
        return values
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid experiments ledger at line {line_number}: {exc}") from exc
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("run_id"), str)
            or not record["run_id"].strip()
        ):
            raise ValueError(f"invalid experiments ledger record at line {line_number}")
        values.add(record["run_id"])
    return values


def validate_run_storage(root: Path, runs_dir: Path, ledger_path: Path, run_ids: set[str]) -> list[str]:
    errors: list[str] = []
    expected_manifests: set[Path] = set()
    for line_number, raw in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        record = json.loads(raw)
        run_id = record["run_id"]
        expected = (runs_dir / run_id / "manifest.json").resolve()
        manifest_value = Path(record["manifest_path"])
        if not manifest_value.is_absolute():
            manifest_value = root / manifest_value
        manifest_is_symlink = manifest_value.is_symlink()
        actual = manifest_value.resolve()
        if actual != expected:
            errors.append(
                f"experiments ledger line {line_number} does not use the canonical manifest path for {run_id}"
            )
        elif not actual.is_file() or manifest_is_symlink:
            errors.append(f"missing or symlinked manifest for {run_id}: {actual}")
        expected_manifests.add(expected)
    for child in runs_dir.iterdir():
        if child.is_symlink() or not child.is_dir():
            errors.append(f"unexpected or symlinked entry in runs directory: {child}")
            continue
        manifest = (child / "manifest.json").resolve()
        if child.name not in run_ids or manifest not in expected_manifests or not manifest.is_file():
            errors.append(f"orphan or incomplete run directory: {child}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--started-at", required=True, help="ISO 8601 timestamp with offset")
    parser.add_argument("--ended-at", required=True, help="ISO 8601 timestamp with offset")
    parser.add_argument("--phase", choices=("smoke", "pilot", "full"), required=True)
    parser.add_argument("--status", choices=("completed", "failed", "aborted"), required=True)
    parser.add_argument("--result-kind", choices=("none", "measured", "synthetic-plumbing"), required=True)
    parser.add_argument(
        "--command", required=True, help="exact command that was or will be run; it is not executed"
    )
    parser.add_argument("--seed", action="append", default=[])
    parser.add_argument("--config", action="append", default=[])
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument(
        "--file-version",
        action="append",
        default=[],
        metavar="PATH=IMMUTABLE_ID",
        help="required for any recorded file larger than 64 MiB",
    )
    parser.add_argument(
        "--resource",
        action="append",
        default=[],
        help="resource, service, hardware, duration, token, or cost fact",
    )
    parser.add_argument("--failure-reason", default="")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not RUN_ID_PATTERN.fullmatch(args.run_id):
        print("error: run ID must be 1-64 safe filename characters", file=sys.stderr)
        return 2
    if not EXPERIMENT_ID_PATTERN.fullmatch(args.experiment_id):
        print("error: experiment ID must be 1-64 safe identifier characters", file=sys.stderr)
        return 2
    if not args.operator.strip():
        print("error: operator must be non-empty", file=sys.stderr)
        return 2
    try:
        started_at = parse_timestamp(args.started_at, "started-at")
        ended_at = parse_timestamp(args.ended_at, "ended-at")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if ended_at < started_at:
        print("error: ended-at precedes started-at", file=sys.stderr)
        return 2
    if args.status in {"failed", "aborted"} and not args.failure_reason.strip():
        print("error: failed or aborted runs require --failure-reason", file=sys.stderr)
        return 2
    base = root / ".research"
    state_path = base / "state.json"
    ledger_path = base / "experiments.jsonl"
    runs_dir = base / "runs"
    if base.is_symlink() or state_path.is_symlink() or ledger_path.is_symlink() or runs_dir.is_symlink():
        print("error: refusing symlinked canonical dossier paths", file=sys.stderr)
        return 2
    if not state_path.is_file() or not ledger_path.is_file():
        print("error: initialize and validate .research first", file=sys.stderr)
        return 2
    if not runs_dir.is_dir():
        print("error: missing .research/runs directory", file=sys.stderr)
        return 2
    dossier_errors = validate_dossier(root)
    if dossier_errors:
        for error in dossier_errors:
            print(f"error: invalid dossier: {error}", file=sys.stderr)
        return 2
    try:
        existing_run_ids = parse_existing_run_ids(ledger_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    storage_errors = validate_run_storage(root, runs_dir, ledger_path, existing_run_ids)
    if storage_errors:
        for error in storage_errors:
            print(f"error: invalid run storage: {error}", file=sys.stderr)
        return 2
    if args.run_id in existing_run_ids:
        print(f"error: run ID already recorded: {args.run_id}", file=sys.stderr)
        return 2

    versions, version_error = parse_versions(args.file_version, root)
    if version_error:
        print(f"error: {version_error}", file=sys.stderr)
        return 2
    referenced_paths = {str(resolve_file(path, root)) for path in args.config + args.input + args.output}
    unknown_versions = sorted(set(versions) - referenced_paths)
    if unknown_versions:
        print(
            f"error: --file-version path is not listed as config, input, or output: {unknown_versions[0]}",
            file=sys.stderr,
        )
        return 2
    config_records = [
        file_record(path, root, versions.get(str(resolve_file(path, root)))) for path in args.config
    ]
    input_records = [
        file_record(path, root, versions.get(str(resolve_file(path, root)))) for path in args.input
    ]
    output_records = [
        file_record(path, root, versions.get(str(resolve_file(path, root)))) for path in args.output
    ]
    for record in config_records + input_records + output_records:
        if (
            record.get("exists")
            and record.get("size_bytes", 0) > MAX_HASH_BYTES
            and not record.get("external_version")
        ):
            print(
                f"error: file exceeds 64 MiB; provide --file-version PATH=IMMUTABLE_ID for {record['path']}",
                file=sys.stderr,
            )
            return 2
    if args.status == "completed":
        for record in config_records + input_records:
            if not record.get("exists"):
                print(f"error: completed run has missing config or input: {record['path']}", file=sys.stderr)
                return 2
    candidate_evidence = (
        args.phase == "full" and args.status == "completed" and args.result_kind == "measured"
    )
    if candidate_evidence and (
        not output_records or any(not record.get("exists") for record in output_records)
    ):
        print("error: a completed full measured run requires at least one existing output", file=sys.stderr)
        return 2

    run_dir = runs_dir / args.run_id
    manifest_path = run_dir / "manifest.json"
    if run_dir.exists() or run_dir.is_symlink():
        print(f"error: immutable run directory already exists: {run_dir}", file=sys.stderr)
        return 2
    manifest = {
        "schema_version": "1.0",
        "run_id": args.run_id,
        "experiment_id": args.experiment_id,
        "operator": args.operator,
        "started_at": started_at.isoformat(timespec="seconds"),
        "ended_at": ended_at.isoformat(timespec="seconds"),
        "recorded_at": now(),
        "phase": args.phase,
        "status": args.status,
        "result_kind": args.result_kind,
        "evidence_eligibility": "candidate_pending_verification"
        if candidate_evidence
        else "not_scientific_evidence",
        "command": args.command,
        "seeds": args.seed,
        "root": str(root),
        "git": git_record(root),
        "environment": {
            "platform": platform.platform(),
            "python": sys.version,
            "executable": sys.executable,
        },
        "configs": config_records,
        "inputs": input_records,
        "outputs": output_records,
        "resources": args.resource,
        "failure_reason": args.failure_reason or None,
        "note": args.note,
    }
    ledger_record = {
        "run_id": args.run_id,
        "experiment_id": args.experiment_id,
        "manifest_path": str(manifest_path.relative_to(root)),
        "phase": args.phase,
        "status": args.status,
        "result_kind": args.result_kind,
        "evidence_eligibility": manifest["evidence_eligibility"],
        "started_at": manifest["started_at"],
        "ended_at": manifest["ended_at"],
        "recorded_at": manifest["recorded_at"],
    }
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest_temp = run_dir / "manifest.json.tmp"
    ledger_temp = ledger_path.with_name(f".{ledger_path.name}.{args.run_id}.tmp")
    manifest_committed = False
    try:
        manifest_temp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        prior_ledger = ledger_path.read_text(encoding="utf-8")
        if prior_ledger and not prior_ledger.endswith("\n"):
            prior_ledger += "\n"
        ledger_temp.write_text(
            prior_ledger + json.dumps(ledger_record, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        os.replace(manifest_temp, manifest_path)
        manifest_committed = True
        os.replace(ledger_temp, ledger_path)
    except OSError as exc:
        for path in (manifest_temp, ledger_temp):
            with contextlib.suppress(FileNotFoundError):
                path.unlink()
        if manifest_committed:
            with contextlib.suppress(FileNotFoundError):
                manifest_path.unlink()
        with contextlib.suppress(OSError):
            run_dir.rmdir()
        print(f"error: failed to commit run manifest and ledger together: {exc}", file=sys.stderr)
        return 2
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
