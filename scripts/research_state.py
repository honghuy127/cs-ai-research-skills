#!/usr/bin/env python3
"""Initialize and structurally validate a project-local research dossier.

This script enforces file and state invariants only. It does not judge novelty,
scientific validity, ethics approval, or whether a result supports a claim.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"
VALID_STAGES = {
    "scoping",
    "literature",
    "proposal",
    "design",
    "implementation",
    "execution",
    "analysis",
    "writing",
    "review",
    "submission",
}
VALID_STATUSES = {
    "not_assessed",
    "proposed",
    "planned",
    "implemented",
    "smoke_tested",
    "pilot_only",
    "executed",
    "analyzed",
    "verified",
    "reported",
    "blocked",
    "dropped",
}
VALID_EVIDENTIAL_STATUSES = {"not_assessed", "insufficient", "supported", "mixed", "contradicted"}
VALID_CLAIM_TYPES = {
    "contextual",
    "novelty",
    "theoretical",
    "empirical",
    "causal",
    "descriptive",
    "normative",
    "performance",
    "efficiency",
    "human-evaluation",
}
VALID_EVIDENCE_VERIFICATIONS = {"metadata-only", "abstract-checked", "full-text-checked", "artifact-checked"}
VALID_PUBLICATION_STATUSES = {"published", "accepted", "preprint", "unpublished", "unknown"}
VALID_PEER_REVIEW_STATUSES = {"peer-reviewed", "not-peer-reviewed", "unknown"}
VALID_RUN_PHASES = {"smoke", "pilot", "full"}
VALID_RUN_STATUSES = {"completed", "failed", "aborted"}
VALID_RESULT_KINDS = {"none", "measured", "synthetic-plumbing"}
VALID_EVIDENCE_ELIGIBILITY = {"candidate_pending_verification", "not_scientific_evidence"}
LEDGERS = ("evidence.jsonl", "claims.jsonl", "experiments.jsonl")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dossier(root: Path) -> Path:
    return root.resolve() / ".research"


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def write_json_atomic(path: Path, value: dict) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def append_decision(
    base: Path,
    decision: str,
    reason: str,
    evidence: list[str],
    alternatives: list[str],
    consequences: list[str],
    owner: str,
    revisit_condition: str,
) -> dict:
    recorded_at = now()
    decision_id = f"DEC-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    with (base / "decisions.md").open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {decision_id} — {recorded_at} — {decision}\n\n")
        handle.write("- Evidence:\n" + "".join(f"  - {item}\n" for item in evidence))
        handle.write("- Alternatives considered:\n" + "".join(f"  - {item}\n" for item in alternatives))
        handle.write(f"- Rationale: {reason}\n")
        handle.write("- Consequences:\n" + "".join(f"  - {item}\n" for item in consequences))
        handle.write(f"- Owner: {owner}\n")
        handle.write(f"- Revisit condition: {revisit_condition}\n")
    return {"id": decision_id, "recorded_at": recorded_at, "summary": decision}


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: project root is not a directory: {root}", file=sys.stderr)
        return 2
    base = dossier(root)
    state_path = base / "state.json"
    if base.is_symlink():
        print(f"error: refusing symlinked dossier path: {base}", file=sys.stderr)
        return 2
    if base.exists() and (not base.is_dir() or any(base.iterdir())):
        print(f"error: non-empty or invalid dossier path already exists: {base}", file=sys.stderr)
        return 2

    base.mkdir(exist_ok=True)
    (base / "runs").mkdir(exist_ok=True)
    created_at = now()
    state = {
        "schema_version": SCHEMA_VERSION,
        "project_id": str(uuid.uuid4()),
        "title": args.title,
        "created_at": created_at,
        "updated_at": created_at,
        "stage": "scoping",
        "stage_status": "proposed",
        "research_questions": [],
        "contribution_type": None,
        "methodology": None,
        "deliverables": [],
        "constraints": {},
        "artifact_index": {},
        "open_risks": [],
        "blockers": [],
        "decision_index": [],
        "next_actions": [],
    }
    (base / "decisions.md").write_text(
        "# Research Decisions\n\n"
        "Append material decisions with evidence, alternatives, rationale, owner, and revisit condition.\n",
        encoding="utf-8",
    )
    for name in LEDGERS:
        (base / name).touch(exist_ok=False)
    decision_entry = append_decision(
        base,
        "Initialize research dossier",
        "Start traceable project state without overwriting project artifacts.",
        [f"Project root inspected: {root}"],
        ["Continue without a dossier"],
        ["Canonical research state will be indexed under .research/"],
        args.owner,
        "Reconcile or retire the dossier if it no longer reflects the project artifacts.",
    )
    state["decision_index"].append(decision_entry)
    write_json_atomic(state_path, state)
    print(base)
    return 0


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    if not path.exists():
        return records, [f"missing ledger: {path}"]
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{line_number}: record must be an object")
            continue
        records.append(value)
    return records, errors


def require_string(record: dict, field: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(record.get(field), str) or not record[field].strip():
        errors.append(f"{prefix} requires non-empty string {field}")


def require_string_list(
    record: dict, field: str, prefix: str, errors: list[str], required: bool = True
) -> None:
    value = record.get(field)
    if value is None and not required:
        return
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{prefix} requires {field} as a list of non-empty strings")


def validate_ledger_record(name: str, record: dict, index: int, errors: list[str]) -> None:
    prefix = f"{name} record {index}"
    if name == "evidence.jsonl":
        for field in ("id", "title", "accessed_at", "verification"):
            require_string(record, field, prefix, errors)
        if record.get("verification") not in VALID_EVIDENCE_VERIFICATIONS:
            errors.append(f"{prefix} has invalid verification: {record.get('verification')!r}")
        for field in ("supports", "challenges", "contextualizes"):
            require_string_list(record, field, prefix, errors, required=False)
        for field in (
            "url",
            "doi",
            "artifact_path",
            "citation_key",
            "locator",
            "source_type",
            "publication_status",
            "peer_review_status",
            "notes",
        ):
            if record.get(field) is not None and (
                not isinstance(record.get(field), str) or not record[field].strip()
            ):
                errors.append(f"{prefix} {field} must be null or a non-empty string")
        if not any(
            isinstance(record.get(field), str) and record[field].strip()
            for field in ("url", "doi", "artifact_path")
        ):
            errors.append(f"{prefix} requires url, doi, or artifact_path")
        if (
            record.get("publication_status") is not None
            and record.get("publication_status") not in VALID_PUBLICATION_STATUSES
        ):
            errors.append(f"{prefix} has invalid publication_status: {record.get('publication_status')!r}")
        if (
            record.get("peer_review_status") is not None
            and record.get("peer_review_status") not in VALID_PEER_REVIEW_STATUSES
        ):
            errors.append(f"{prefix} has invalid peer_review_status: {record.get('peer_review_status')!r}")
    elif name == "claims.jsonl":
        for field in (
            "id",
            "text",
            "claim_type",
            "lifecycle_state",
            "evidential_status",
            "scope",
            "updated_at",
        ):
            require_string(record, field, prefix, errors)
        if record.get("lifecycle_state") not in VALID_STATUSES:
            errors.append(f"{prefix} has invalid lifecycle_state: {record.get('lifecycle_state')!r}")
        if record.get("evidential_status") not in VALID_EVIDENTIAL_STATUSES:
            errors.append(f"{prefix} has invalid evidential_status: {record.get('evidential_status')!r}")
        if record.get("claim_type") not in VALID_CLAIM_TYPES:
            errors.append(f"{prefix} has invalid claim type: {record.get('claim_type')!r}")
        for field in ("evidence_ids", "run_ids", "artifact_paths", "caveats"):
            require_string_list(record, field, prefix, errors)
        for field in ("verification_run_ids", "verification_artifact_paths"):
            require_string_list(record, field, prefix, errors, required=False)
    elif name == "experiments.jsonl":
        for field in (
            "run_id",
            "experiment_id",
            "manifest_path",
            "phase",
            "status",
            "result_kind",
            "evidence_eligibility",
            "started_at",
            "ended_at",
            "recorded_at",
        ):
            require_string(record, field, prefix, errors)
        enum_fields = {
            "phase": VALID_RUN_PHASES,
            "status": VALID_RUN_STATUSES,
            "result_kind": VALID_RESULT_KINDS,
            "evidence_eligibility": VALID_EVIDENCE_ELIGIBILITY,
        }
        for field, allowed in enum_fields.items():
            if record.get(field) not in allowed:
                errors.append(f"{prefix} has invalid {field}: {record.get(field)!r}")


def validate(root: Path) -> list[str]:
    base = dossier(root)
    errors: list[str] = []
    if base.is_symlink():
        return [f"refusing symlinked dossier path: {base}"]
    if not base.is_dir():
        return [f"missing dossier directory: {base}"]
    protected_paths = [base / "state.json", base / "decisions.md", base / "runs"] + [
        base / name for name in LEDGERS
    ]
    symlinked = [str(path) for path in protected_paths if path.is_symlink()]
    if symlinked:
        return [f"refusing symlinked canonical dossier path: {path}" for path in symlinked]
    try:
        state = load_json(base / "state.json")
    except ValueError as exc:
        return [str(exc)]

    required = {
        "schema_version",
        "project_id",
        "title",
        "created_at",
        "updated_at",
        "stage",
        "stage_status",
        "research_questions",
        "contribution_type",
        "methodology",
        "deliverables",
        "constraints",
        "artifact_index",
        "open_risks",
        "blockers",
        "decision_index",
        "next_actions",
    }
    missing = sorted(required - state.keys())
    if missing:
        errors.append(f"state.json missing fields: {', '.join(missing)}")
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {state.get('schema_version')!r}")
    if state.get("stage") not in VALID_STAGES:
        errors.append(f"invalid stage: {state.get('stage')!r}")
    if state.get("stage_status") not in VALID_STATUSES:
        errors.append(f"invalid stage_status: {state.get('stage_status')!r}")
    for field in ("schema_version", "project_id", "title", "created_at", "updated_at"):
        if not isinstance(state.get(field), str) or not state[field].strip():
            errors.append(f"state.json requires non-empty string {field}")
    for field in (
        "research_questions",
        "deliverables",
        "open_risks",
        "blockers",
        "decision_index",
        "next_actions",
    ):
        if not isinstance(state.get(field), list):
            errors.append(f"state.json requires list {field}")
    for field in ("constraints", "artifact_index"):
        if not isinstance(state.get(field), dict):
            errors.append(f"state.json requires object {field}")
    for field in ("contribution_type", "methodology"):
        if state.get(field) is not None and not isinstance(state.get(field), str):
            errors.append(f"state.json {field} must be null or a string")
    if isinstance(state.get("decision_index"), list):
        for index, item in enumerate(state["decision_index"], start=1):
            if not isinstance(item, dict) or any(
                not isinstance(item.get(field), str) or not item[field].strip()
                for field in ("id", "recorded_at", "summary")
            ):
                errors.append(f"state.json decision_index entry {index} is invalid")

    for name in LEDGERS:
        records, ledger_errors = read_jsonl(base / name)
        errors.extend(ledger_errors)
        seen: set[str] = set()
        superseded: set[str] = set()
        key = "run_id" if name == "experiments.jsonl" else "id"
        for index, record in enumerate(records, start=1):
            validate_ledger_record(name, record, index, errors)
            identifier = record.get(key)
            if not isinstance(identifier, str) or not identifier.strip():
                errors.append(f"{name} record {index} lacks non-empty {key}")
            elif identifier in seen:
                errors.append(f"{name} contains duplicate {key}: {identifier}")
            else:
                seen.add(identifier)
            supersedes = record.get("supersedes")
            if supersedes is not None:
                if not isinstance(supersedes, str) or not supersedes.strip():
                    errors.append(f"{name} record {index} has invalid supersedes")
                elif supersedes == identifier:
                    errors.append(f"{name} record {index} supersedes itself: {supersedes}")
                elif supersedes not in seen:
                    errors.append(
                        f"{name} record {index} supersedes a missing or later same-ledger record: {supersedes}"
                    )
                elif supersedes in superseded:
                    errors.append(
                        f"{name} record {index} creates a second supersession branch for: {supersedes}"
                    )
                else:
                    superseded.add(supersedes)
    if not (base / "decisions.md").exists():
        errors.append(f"missing decision log: {base / 'decisions.md'}")
    if not (base / "runs").is_dir():
        errors.append(f"missing runs directory: {base / 'runs'}")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate(Path(args.root))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Research dossier is structurally valid.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.root)
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    base = dossier(root)
    state = load_json(base / "state.json")
    counts = {}
    for name in LEDGERS:
        records, _ = read_jsonl(base / name)
        counts[name.removesuffix(".jsonl")] = len(records)
    summary = {
        "project_id": state["project_id"],
        "title": state["title"],
        "stage": state["stage"],
        "stage_status": state["stage_status"],
        "updated_at": state["updated_at"],
        "record_counts": counts,
        "blockers": state.get("blockers", []),
        "next_actions": state.get("next_actions", []),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


UPDATE_LIST_FIELDS = {
    "research_question": "research_questions",
    "deliverable": "deliverables",
    "open_risk": "open_risks",
    "blocker": "blockers",
    "next_action": "next_actions",
}


def cmd_update(args: argparse.Namespace) -> int:
    root = Path(args.root)
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    base = dossier(root)
    state = load_json(base / "state.json")
    changed: list[str] = []
    if args.title is not None:
        if not args.title.strip():
            print("error: title must be non-empty", file=sys.stderr)
            return 2
        state["title"] = args.title
        changed.append("title")
    for option in ("contribution_type", "methodology"):
        value = getattr(args, option)
        if value is not None:
            state[option] = value.strip() or None
            changed.append(option)
    for option, field in UPDATE_LIST_FIELDS.items():
        values = getattr(args, option)
        if values is not None:
            cleaned = [item for item in values if item.strip()]
            state[field] = cleaned
            changed.append(field)
    if not changed:
        print("error: no update options were provided", file=sys.stderr)
        return 2
    state["updated_at"] = now()
    write_json_atomic(base / "state.json", state)
    remaining = validate(root)
    if remaining:
        for error in remaining:
            print(f"ERROR: {error}")
        return 1
    print(f"updated: {', '.join(changed)}")
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    root = Path(args.root)
    base = dossier(root)
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.stage not in VALID_STAGES or args.status not in VALID_STATUSES:
        print("error: invalid stage or status", file=sys.stderr)
        return 2
    state = load_json(base / "state.json")
    previous = f"{state['stage']} / {state['stage_status']}"
    state["stage"] = args.stage
    state["stage_status"] = args.status
    state["updated_at"] = now()
    decision_entry = append_decision(
        base,
        f"Transition {previous} → {args.stage} / {args.status}",
        args.reason,
        args.evidence,
        args.alternative,
        args.consequence,
        args.owner,
        args.revisit_condition,
    )
    state["decision_index"].append(decision_entry)
    write_json_atomic(base / "state.json", state)
    print(f"{args.stage} / {args.status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="initialize .research without overwriting existing state"
    )
    init_parser.add_argument("--root", default=".")
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument("--owner", required=True)
    init_parser.set_defaults(func=cmd_init)

    validate_parser = subparsers.add_parser("validate", help="validate structural invariants")
    validate_parser.add_argument("--root", default=".")
    validate_parser.set_defaults(func=cmd_validate)

    status_parser = subparsers.add_parser("status", help="print a compact project summary")
    status_parser.add_argument("--root", default=".")
    status_parser.set_defaults(func=cmd_status)

    update_parser = subparsers.add_parser(
        "update",
        help="update state.json index fields; each repeated list option replaces the whole list",
        description=(
            "Update common state.json index fields. Repeatable options replace the entire "
            "stored list. Edit constraints or artifact_index directly in state.json, then "
            "run validate."
        ),
    )
    update_parser.add_argument("--root", default=".")
    update_parser.add_argument("--title")
    update_parser.add_argument(
        "--contribution-type", dest="contribution_type", help="empty string clears the field"
    )
    update_parser.add_argument("--methodology", help="empty string clears the field")
    update_parser.add_argument("--research-question", dest="research_question", action="append")
    update_parser.add_argument("--deliverable", action="append")
    update_parser.add_argument("--open-risk", dest="open_risk", action="append")
    update_parser.add_argument("--blocker", action="append")
    update_parser.add_argument("--next-action", dest="next_action", action="append")
    update_parser.set_defaults(func=cmd_update)

    transition_parser = subparsers.add_parser("transition", help="record a justified stage transition")
    transition_parser.add_argument("--root", default=".")
    transition_parser.add_argument("--stage", required=True, choices=sorted(VALID_STAGES))
    transition_parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    transition_parser.add_argument("--reason", required=True)
    transition_parser.add_argument("--evidence", action="append", required=True)
    transition_parser.add_argument("--alternative", action="append", required=True)
    transition_parser.add_argument("--consequence", action="append", required=True)
    transition_parser.add_argument("--owner", required=True)
    transition_parser.add_argument("--revisit-condition", required=True)
    transition_parser.set_defaults(func=cmd_transition)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
