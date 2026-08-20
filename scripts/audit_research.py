#!/usr/bin/env python3
"""Audit structural traceability across a project-local research dossier.

This audit surfaces missing links and placeholders. It cannot certify novelty,
correctness, statistical validity, ethics compliance, or reproducibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from research_state import (
    VALID_EVIDENCE_ELIGIBILITY,
    VALID_RESULT_KINDS,
    VALID_RUN_PHASES,
    VALID_RUN_STATUSES,
)
from research_state import (
    validate as validate_dossier,
)

PLACEHOLDERS = ("[CITATION NEEDED]", "[EVIDENCE NEEDED]", "[RESULT PENDING]")
EVIDENCE_BEARING_STATUSES = {"supported", "mixed", "contradicted"}
EXECUTION_BEARING_STATES = {"executed", "analyzed", "verified", "reported"}
INDEPENDENT_CHECK_STATES = {"verified", "reported"}
EMPIRICAL_TYPES = {"empirical", "causal", "performance", "efficiency", "human-evaluation"}
SUPPORTED_MANIFEST_SCHEMAS = {"1.0", "1.1"}
MAX_HASH_BYTES = 64 * 1024 * 1024


def load_jsonl(path: Path) -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    findings: list[dict] = []
    if not path.exists():
        return records, [{"severity": "error", "code": "missing-ledger", "message": str(path)}]
    if path.is_symlink():
        return records, [{"severity": "error", "code": "symlinked-ledger", "message": str(path)}]
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            findings.append(
                {"severity": "error", "code": "invalid-jsonl", "message": f"{path}:{line_number}: {exc}"}
            )
            continue
        if not isinstance(value, dict):
            findings.append(
                {
                    "severity": "error",
                    "code": "invalid-record",
                    "message": f"{path}:{line_number}: expected object",
                }
            )
            continue
        records.append(value)
    return records, findings


def add(findings: list[dict], severity: str, code: str, message: str, record_id: str | None = None) -> None:
    item = {"severity": severity, "code": code, "message": message}
    if record_id:
        item["record_id"] = record_id
    findings.append(item)


def scan_file(path: Path, findings: list[dict], warn_non_text: bool = True) -> None:
    if not path.is_file():
        add(findings, "error", "missing-scan-target", str(path))
        return
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        if warn_non_text:
            add(findings, "warning", "non-text-scan-target", str(path))
        return
    for token in PLACEHOLDERS:
        for line_number, line in enumerate(text.splitlines(), start=1):
            if token in line:
                add(findings, "error", "unresolved-placeholder", f"{path}:{line_number}: {token}")


def superseded_ids(records: list[dict]) -> set[str]:
    return {
        record["supersedes"]
        for record in records
        if isinstance(record.get("supersedes"), str) and record["supersedes"].strip()
    }


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_path(raw_path: str, root: Path) -> Path:
    path_text = raw_path.split("#", 1)[0]
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    return path


def audit_artifact_paths(
    raw_paths: list[str],
    root: Path,
    findings: list[dict],
    code: str,
    record_id: str | None,
    require_file: bool = False,
) -> None:
    for raw_path in raw_paths:
        if not isinstance(raw_path, str) or not raw_path.strip():
            add(findings, "error", code, f"invalid artifact path: {raw_path!r}", record_id)
            continue
        if not raw_path.split("#", 1)[0]:
            add(
                findings, "error", code, f"artifact path has no filesystem component: {raw_path!r}", record_id
            )
            continue
        path = artifact_path(raw_path, root)
        if path.is_symlink() or not path.exists() or (require_file and not path.is_file()):
            add(findings, "error", code, str(path), record_id)


def audit_file_records(
    records: object,
    category: str,
    root: Path,
    findings: list[dict],
    run_id: str | None,
    required: bool,
) -> None:
    if not isinstance(records, list):
        return
    if required and not records and category == "outputs":
        add(findings, "error", "candidate-run-without-outputs", "no outputs recorded", run_id)
    for record in records:
        if not isinstance(record, dict):
            add(findings, "error", f"invalid-{category}-record", repr(record), run_id)
            continue
        raw_path = record.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            add(findings, "error", f"invalid-{category}-path", repr(record), run_id)
            continue
        path = Path(raw_path)
        if not path.is_absolute():
            path = root / path
        recorded_exists = record.get("exists")
        if not isinstance(recorded_exists, bool):
            add(findings, "error", f"invalid-{category}-existence", repr(record), run_id)
            continue
        if required and not recorded_exists:
            add(findings, "error", f"required-{category}-missing-at-capture", str(path), run_id)
            continue
        if not recorded_exists:
            continue
        if path.is_symlink() or not path.is_file():
            add(findings, "error", f"recorded-{category}-no-longer-exists", str(path), run_id)
            continue
        current_size = path.stat().st_size
        if record.get("size_bytes") != current_size:
            add(findings, "error", f"recorded-{category}-size-changed", str(path), run_id)
            continue
        recorded_hash = record.get("sha256")
        if current_size <= MAX_HASH_BYTES:
            if not isinstance(recorded_hash, str) or not recorded_hash:
                add(findings, "error", f"recorded-{category}-missing-hash", str(path), run_id)
            elif hash_file(path) != recorded_hash:
                add(findings, "error", f"recorded-{category}-hash-changed", str(path), run_id)
        elif not record.get("external_version"):
            add(findings, "error", f"recorded-large-{category}-unversioned", str(path), run_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--scan", action="append", default=[], help="manuscript or proposal text file to scan"
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    base = root / ".research"
    findings: list[dict] = []
    for error in validate_dossier(root):
        add(findings, "error", "invalid-dossier", error)
    if base.is_symlink():
        add(findings, "error", "symlinked-dossier", str(base))
        evidence, claims, experiments = [], [], []
    else:
        evidence, evidence_findings = load_jsonl(base / "evidence.jsonl")
        claims, claim_findings = load_jsonl(base / "claims.jsonl")
        experiments, experiment_findings = load_jsonl(base / "experiments.jsonl")
        findings.extend(evidence_findings + claim_findings + experiment_findings)

    evidence_by_id = {item.get("id"): item for item in evidence if isinstance(item.get("id"), str)}
    claim_by_id = {item.get("id"): item for item in claims if isinstance(item.get("id"), str)}
    evidence_ids = set(evidence_by_id)
    claim_ids = set(claim_by_id)
    run_ids = {item.get("run_id") for item in experiments if isinstance(item.get("run_id"), str)}
    superseded_evidence = superseded_ids(evidence)
    superseded_claims = superseded_ids(claims)

    for item in evidence:
        identifier = item.get("id") if isinstance(item.get("id"), str) else None
        if identifier in superseded_evidence:
            continue
        for field in ("id", "title", "accessed_at", "verification"):
            if not item.get(field):
                add(findings, "error", "incomplete-evidence", f"missing {field}", identifier)
        if not any(item.get(field) for field in ("url", "doi", "artifact_path")):
            add(
                findings,
                "error",
                "incomplete-evidence",
                "missing authoritative source or artifact locator",
                identifier,
            )
        if item.get("verification") == "metadata-only" and (item.get("supports") or item.get("challenges")):
            add(
                findings,
                "error",
                "metadata-used-substantively",
                "metadata-only source is linked as substantive evidence",
                identifier,
            )
        if item.get("verification") in {"full-text-checked", "artifact-checked"} and not item.get("locator"):
            add(
                findings,
                "error",
                "verified-evidence-without-locator",
                "verified source lacks a passage, section, theorem, table, or artifact locator",
                identifier,
            )
        if isinstance(item.get("artifact_path"), str):
            audit_artifact_paths(
                [item["artifact_path"]], root, findings, "missing-evidence-artifact", identifier
            )
        for relation in ("supports", "challenges", "contextualizes"):
            targets = item.get(relation) if isinstance(item.get(relation), list) else []
            for claim_id in targets:
                if claim_id not in claim_ids:
                    add(findings, "error", "unknown-claim-id", f"{relation}: {claim_id}", identifier)
                    continue
                if claim_id in superseded_claims:
                    continue
                if relation == "contextualizes":
                    continue
                linked_sources = claim_by_id[claim_id].get("evidence_ids")
                if not isinstance(linked_sources, list) or identifier not in linked_sources:
                    add(
                        findings,
                        "error",
                        "missing-claim-evidence-backlink",
                        f"{claim_id} does not link {identifier}",
                        identifier,
                    )

    runs_dir = base / "runs"
    runs_root = None if runs_dir.is_symlink() else runs_dir.resolve()
    if runs_dir.is_symlink():
        add(findings, "error", "symlinked-runs-directory", str(runs_dir))

    run_eligibility: dict[str, str] = {}
    for item in experiments:
        run_id = item.get("run_id") if isinstance(item.get("run_id"), str) else None
        manifest_value = item.get("manifest_path")
        if not manifest_value:
            add(findings, "error", "missing-manifest-path", "experiment record has no manifest", run_id)
            continue
        manifest_path = Path(manifest_value)
        if not manifest_path.is_absolute():
            manifest_path = root / manifest_path
        if manifest_path.is_symlink():
            add(findings, "error", "symlinked-manifest", str(manifest_path), run_id)
            continue
        manifest_path = manifest_path.resolve()
        if runs_root is None:
            continue
        expected_manifest_path = (runs_dir / str(run_id) / "manifest.json").resolve() if run_id else None
        if expected_manifest_path is None or manifest_path != expected_manifest_path:
            add(findings, "error", "noncanonical-manifest-path", str(manifest_path), run_id)
            continue
        try:
            manifest_path.relative_to(runs_root)
        except ValueError:
            add(findings, "error", "manifest-outside-runs", str(manifest_path), run_id)
            continue
        if not manifest_path.is_file():
            add(findings, "error", "missing-manifest", str(manifest_path), run_id)
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            add(findings, "error", "invalid-manifest", f"{manifest_path}: {exc}", run_id)
            continue
        if not isinstance(manifest, dict):
            add(findings, "error", "invalid-manifest", f"{manifest_path}: expected JSON object", run_id)
            continue
        for field in (
            "schema_version",
            "run_id",
            "experiment_id",
            "operator",
            "started_at",
            "ended_at",
            "recorded_at",
            "phase",
            "status",
            "result_kind",
            "evidence_eligibility",
            "command",
        ):
            if not isinstance(manifest.get(field), str) or not manifest[field].strip():
                add(
                    findings,
                    "error",
                    "incomplete-manifest",
                    f"missing or invalid {field}: {manifest_path}",
                    run_id,
                )
        for field in ("seeds", "configs", "inputs", "outputs", "resources"):
            if not isinstance(manifest.get(field), list):
                add(
                    findings,
                    "error",
                    "incomplete-manifest",
                    f"{field} must be a list: {manifest_path}",
                    run_id,
                )
        environment_field = "environment" if manifest.get("schema_version") == "1.0" else "capture_environment"
        for field in ("git", environment_field):
            if not isinstance(manifest.get(field), dict):
                add(
                    findings,
                    "error",
                    "incomplete-manifest",
                    f"{field} must be an object: {manifest_path}",
                    run_id,
                )
        if manifest.get("schema_version") not in SUPPORTED_MANIFEST_SCHEMAS:
            add(findings, "error", "unsupported-manifest-schema", str(manifest.get("schema_version")), run_id)
        enum_fields = {
            "phase": VALID_RUN_PHASES,
            "status": VALID_RUN_STATUSES,
            "result_kind": VALID_RESULT_KINDS,
            "evidence_eligibility": VALID_EVIDENCE_ELIGIBILITY,
        }
        for field, allowed in enum_fields.items():
            if manifest.get(field) not in allowed:
                add(findings, "error", "invalid-manifest-enum", f"{field}: {manifest.get(field)!r}", run_id)
        if manifest.get("run_id") != run_id:
            add(findings, "error", "manifest-run-mismatch", str(manifest_path), run_id)
        for field in (
            "experiment_id",
            "started_at",
            "ended_at",
            "phase",
            "status",
            "result_kind",
            "evidence_eligibility",
        ):
            if item.get(field) != manifest.get(field):
                add(
                    findings,
                    "error",
                    "ledger-manifest-mismatch",
                    f"{field}: ledger={item.get(field)!r}, manifest={manifest.get(field)!r}",
                    run_id,
                )
        try:
            started_at = datetime.fromisoformat(str(manifest.get("started_at", "")).replace("Z", "+00:00"))
            ended_at = datetime.fromisoformat(str(manifest.get("ended_at", "")).replace("Z", "+00:00"))
            if started_at.tzinfo is None or ended_at.tzinfo is None or ended_at < started_at:
                raise ValueError
        except ValueError:
            add(findings, "error", "invalid-run-timestamps", str(manifest_path), run_id)
        if manifest.get("status") in {"failed", "aborted"} and not manifest.get("failure_reason"):
            add(findings, "error", "run-failure-without-reason", str(manifest_path), run_id)
        if (
            manifest.get("result_kind") == "synthetic-plumbing"
            and manifest.get("evidence_eligibility") != "not_scientific_evidence"
        ):
            add(findings, "error", "synthetic-evidence-promotion", str(manifest_path), run_id)
        expected_eligibility = (
            "candidate_pending_verification"
            if manifest.get("phase") == "full"
            and manifest.get("status") == "completed"
            and manifest.get("result_kind") == "measured"
            else "not_scientific_evidence"
        )
        if manifest.get("evidence_eligibility") != expected_eligibility:
            add(
                findings,
                "error",
                "invalid-evidence-eligibility",
                f"expected {expected_eligibility}: {manifest_path}",
                run_id,
            )
        elif isinstance(run_id, str) and manifest.get("run_id") == run_id:
            run_eligibility[run_id] = expected_eligibility
        completed = manifest.get("status") == "completed"
        candidate = manifest.get("evidence_eligibility") == "candidate_pending_verification"
        audit_file_records(manifest.get("configs"), "configs", root, findings, run_id, required=completed)
        audit_file_records(manifest.get("inputs"), "inputs", root, findings, run_id, required=completed)
        audit_file_records(manifest.get("outputs"), "outputs", root, findings, run_id, required=candidate)

        git = manifest.get("git")
        if isinstance(git, dict) and git.get("available") is True and git.get("dirty") is True:
            dirty_files = git.get("dirty_file_hashes")
            if git.get("dirty_snapshot_complete") is not True:
                add(findings, "error", "incomplete-dirty-git-snapshot", str(manifest_path), run_id)
            if not isinstance(dirty_files, list):
                add(findings, "error", "dirty-git-without-content-snapshot", str(manifest_path), run_id)
            else:
                for dirty_file in dirty_files:
                    if (
                        not isinstance(dirty_file, dict)
                        or not isinstance(dirty_file.get("path"), str)
                        or dirty_file.get("kind") not in {"file", "symlink", "deleted-or-unavailable"}
                    ):
                        add(findings, "error", "invalid-dirty-git-record", repr(dirty_file), run_id)
                    elif dirty_file.get("kind") == "file" and not isinstance(
                        dirty_file.get("size_bytes"), int
                    ):
                        add(findings, "error", "dirty-git-file-without-size", repr(dirty_file), run_id)
                    elif (
                        dirty_file.get("kind") == "file"
                        and dirty_file.get("size_bytes", 0) <= MAX_HASH_BYTES
                        and not isinstance(dirty_file.get("sha256"), str)
                    ):
                        add(findings, "error", "dirty-git-file-without-hash", repr(dirty_file), run_id)
                    elif (
                        dirty_file.get("kind") == "file"
                        and dirty_file.get("size_bytes", 0) > MAX_HASH_BYTES
                        and not dirty_file.get("hash_note")
                    ):
                        add(
                            findings,
                            "error",
                            "dirty-large-file-without-provenance-note",
                            repr(dirty_file),
                            run_id,
                        )
                    elif (
                        dirty_file.get("kind") == "file" and dirty_file.get("size_bytes", 0) > MAX_HASH_BYTES
                    ):
                        add(
                            findings,
                            "warning",
                            "dirty-large-file-not-content-hashed",
                            str(dirty_file.get("path")),
                            run_id,
                        )
                    elif dirty_file.get("kind") == "symlink" and not isinstance(
                        dirty_file.get("target"), str
                    ):
                        add(findings, "error", "dirty-git-symlink-without-target", repr(dirty_file), run_id)

    if runs_root is not None and runs_dir.is_dir():
        ledger_manifests: set[Path] = set()
        for item in experiments:
            manifest_value = item.get("manifest_path")
            if isinstance(manifest_value, str):
                path = Path(manifest_value)
                if not path.is_absolute():
                    path = root / path
                ledger_manifests.add(path.resolve())
        for run_dir in runs_dir.iterdir():
            if run_dir.is_symlink():
                add(findings, "error", "symlinked-run-directory", str(run_dir))
                continue
            if not run_dir.is_dir():
                add(findings, "error", "unexpected-file-in-runs", str(run_dir))
                continue
            candidate_manifest = (run_dir / "manifest.json").resolve()
            if not candidate_manifest.is_file():
                add(findings, "error", "orphan-run-directory", str(run_dir))
            elif candidate_manifest not in ledger_manifests:
                add(findings, "error", "unledgered-run-manifest", str(candidate_manifest))

    auto_scanned: set[Path] = set()
    for item in claims:
        identifier = item.get("id") if isinstance(item.get("id"), str) else None
        if identifier in superseded_claims:
            continue
        lifecycle_state = item.get("lifecycle_state")
        evidential_status = item.get("evidential_status")
        linked_evidence = item.get("evidence_ids") if isinstance(item.get("evidence_ids"), list) else []
        linked_runs = item.get("run_ids") if isinstance(item.get("run_ids"), list) else []
        artifact_paths = item.get("artifact_paths") if isinstance(item.get("artifact_paths"), list) else []
        evidence_bearing = (
            evidential_status in EVIDENCE_BEARING_STATUSES or lifecycle_state in EXECUTION_BEARING_STATES
        )
        if evidence_bearing and not linked_evidence and not linked_runs and not artifact_paths:
            add(
                findings,
                "error",
                "untraced-evidence-bearing-claim",
                "claim has no linked evidence, run, or artifact",
                identifier,
            )
        for source_id in linked_evidence:
            if source_id not in evidence_ids:
                add(findings, "error", "unknown-evidence-id", str(source_id), identifier)
                continue
            if source_id in superseded_evidence:
                add(
                    findings,
                    "warning",
                    "claim-links-superseded-evidence",
                    f"claim links superseded evidence record: {source_id}",
                    identifier,
                )
                continue
            source = evidence_by_id[source_id]
            if source.get("verification") == "metadata-only":
                add(findings, "error", "claim-uses-metadata-as-evidence", str(source_id), identifier)
            relations = []
            for relation in ("supports", "challenges", "contextualizes"):
                values = source.get(relation)
                if isinstance(values, list):
                    relations.extend(values)
            if identifier not in relations:
                add(
                    findings,
                    "error",
                    "missing-evidence-claim-relation",
                    f"{source_id} does not classify its relation to {identifier}",
                    identifier,
                )
        for linked_run_id in linked_runs:
            if linked_run_id not in run_ids:
                add(findings, "error", "unknown-run-id", str(linked_run_id), identifier)
        audit_artifact_paths(artifact_paths, root, findings, "missing-claim-artifact", identifier)
        requires_internal_runs = lifecycle_state in EXECUTION_BEARING_STATES
        if item.get("claim_type") in EMPIRICAL_TYPES and evidence_bearing and requires_internal_runs:
            if not linked_runs:
                add(
                    findings,
                    "error",
                    "empirical-claim-without-run",
                    "evidence-bearing empirical claim lacks a run ID",
                    identifier,
                )
            for linked_run_id in linked_runs:
                if run_eligibility.get(linked_run_id) != "candidate_pending_verification":
                    add(
                        findings,
                        "error",
                        "ineligible-run-supports-claim",
                        f"run is not a completed, measured, full-phase candidate: {linked_run_id}",
                        identifier,
                    )
        if item.get("claim_type") in EMPIRICAL_TYPES and lifecycle_state in INDEPENDENT_CHECK_STATES:
            verification_runs = (
                item.get("verification_run_ids") if isinstance(item.get("verification_run_ids"), list) else []
            )
            verification_artifacts = (
                item.get("verification_artifact_paths")
                if isinstance(item.get("verification_artifact_paths"), list)
                else []
            )
            if not verification_runs and not verification_artifacts:
                add(
                    findings,
                    "error",
                    "verified-claim-without-independent-check",
                    "verified empirical claim lacks a distinct verification run or verification artifact",
                    identifier,
                )
            for verification_run_id in verification_runs:
                if verification_run_id in linked_runs:
                    add(
                        findings,
                        "error",
                        "verification-run-not-independent",
                        str(verification_run_id),
                        identifier,
                    )
                elif run_eligibility.get(verification_run_id) != "candidate_pending_verification":
                    add(findings, "error", "invalid-verification-run", str(verification_run_id), identifier)
            for raw_path in verification_artifacts:
                audit_artifact_paths(
                    [raw_path], root, findings, "missing-verification-artifact", identifier, require_file=True
                )
        if lifecycle_state == "reported" and not artifact_paths:
            add(
                findings,
                "error",
                "reported-claim-without-location",
                "reported claim has no manuscript or artifact path",
                identifier,
            )
        elif lifecycle_state == "reported":
            reported_files = [
                artifact_path(path, root)
                for path in artifact_paths
                if isinstance(path, str) and path.split("#", 1)[0]
            ]
            if not any(path.is_file() and not path.is_symlink() for path in reported_files):
                add(
                    findings,
                    "error",
                    "reported-claim-without-file-location",
                    "reported claim lacks a concrete manuscript or deliverable file",
                    identifier,
                )
            for path in reported_files:
                resolved = path.resolve()
                if resolved.is_file() and not path.is_symlink() and resolved not in auto_scanned:
                    auto_scanned.add(resolved)
                    scan_file(resolved, findings, warn_non_text=False)

    for raw_path in args.scan:
        path = Path(raw_path)
        if not path.is_absolute():
            path = root / path
        resolved = path.resolve()
        if resolved in auto_scanned:
            continue
        scan_file(resolved, findings)

    counts = {
        severity: sum(1 for item in findings if item["severity"] == severity)
        for severity in ("error", "warning")
    }
    report = {
        "root": str(root),
        "scope": "structural traceability only",
        "counts": counts,
        "findings": findings,
        "certifies_scientific_validity": False,
    }
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for item in findings:
            suffix = f" [{item['record_id']}]" if item.get("record_id") else ""
            print(f"{item['severity'].upper()} {item['code']}{suffix}: {item['message']}")
        print(f"errors={counts['error']} warnings={counts['warning']}")
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
