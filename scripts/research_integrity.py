"""Evaluate declarative checks against a stable, read-only project snapshot."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path, PureWindowsPath

from research_contract import hash_file


def unique_keys(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def parse_json(data: bytes):
    def invalid_constant(value: str):
        raise ValueError(f"invalid JSON number {value}")

    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=unique_keys,
            parse_float=Decimal,
            parse_constant=invalid_constant,
        )
    except InvalidOperation as exc:
        raise ValueError("decimal exponent out of range") from exc


def fields(value: object, expected: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"expected fields {sorted(expected)}")


def project_file(root: Path, name: str) -> Path:
    if (
        not isinstance(name, str)
        or not name
        or PureWindowsPath(name).anchor
        or chr(92) in name
        or any(part in {"", ".", ".."} for part in name.split("/"))
    ):
        raise ValueError(f"expected project-relative file: {name!r}")
    path = root
    for part in name.split("/"):
        path = path / part
        if path.is_symlink():
            raise ValueError(f"symlink in {name}")
    if not path.is_file():
        raise ValueError(f"missing regular file {name}")
    return path


def split_ids(path: Path) -> set[str]:
    values = parse_json(path.read_bytes())
    if not isinstance(values, list) or not values:
        raise ValueError(f"{path.name}: expected nonempty JSON array")
    if any(not isinstance(v, str) or not v or v != v.strip() for v in values):
        raise ValueError(f"{path.name}: expected canonical string IDs")
    return set(values)


def check_one(root: Path, rule: dict) -> None:
    kind = rule.get("kind")
    base = {"kind", "id"}
    if kind == "sha256":
        fields(rule, base | {"path", "digest"})
        digest = rule["digest"]
        if not isinstance(digest, str) or not re.fullmatch("[a-f0-9]{64}", digest):
            raise ValueError("expected lowercase SHA-256")
        if hash_file(project_file(root, rule["path"])) != digest:
            raise ValueError(f"{rule['path']}: SHA-256 mismatch")
    elif kind == "disjoint":
        fields(rule, base | {"left", "right"})
        left = split_ids(project_file(root, rule["left"]))
        right = split_ids(project_file(root, rule["right"]))
        overlap = len(left & right)
        if overlap:
            raise ValueError(
                f"{rule['left']} and {rule['right']}: {overlap} shared IDs"
            )
    elif kind == "range":
        fields(rule, base | {"path", "key", "min", "max"})
        data = parse_json(project_file(root, rule["path"]).read_bytes())
        key = rule["key"]
        if not isinstance(key, str) or not isinstance(data, dict) or key not in data:
            raise ValueError(f"{rule['path']}: missing observable {key!r}")
        value, low, high = data[key], rule["min"], rule["max"]
        if not all(type(v) in (int, Decimal) for v in (value, low, high)) or low > high:
            raise ValueError(f"{key}: expected numeric value and ordered bounds")
        if not low <= value <= high:
            raise ValueError(f"{key}: {value} outside [{low}, {high}]")
    else:
        raise ValueError(f"unknown check kind {kind!r}")


def validate_requirements(spec: dict, check_ids: set[str]) -> list[dict]:
    expected = {"id", "artifacts", "checks", "claims"}
    if not isinstance(spec.get("requirements"), list) or not spec["requirements"]:
        raise ValueError("version 2 requires a nonempty requirements array")
    requirements = []
    requirement_ids = set()
    referenced_checks = set()
    for requirement in spec["requirements"]:
        if not isinstance(requirement, dict):
            raise TypeError("expected requirement object")
        status = requirement.get("status", "automated")
        fields(
            requirement,
            expected if status == "automated" else expected | {"status", "reason"},
        )
        if status not in {"automated", "manual", "not_assessed"}:
            raise ValueError("unknown requirement status")
        name = requirement["id"]
        artifacts = requirement["artifacts"]
        checks = requirement["checks"]
        claims = requirement["claims"]
        if not isinstance(name, str) or not name.strip() or name in requirement_ids:
            raise ValueError("expected unique nonempty requirement ID")
        if (
            not isinstance(artifacts, list)
            or any(not isinstance(artifact, str) for artifact in artifacts)
            or not isinstance(checks, list)
            or any(not isinstance(check, str) for check in checks)
            or not isinstance(claims, list)
            or any(not isinstance(claim, str) or not claim.strip() for claim in claims)
        ):
            raise ValueError(f"{name}: expected string artifact, check, and claim arrays")
        if len(set(checks)) != len(checks):
            raise ValueError(f"{name}: duplicate check reference")
        if status == "automated" and not checks:
            raise ValueError(f"{name}: automated requirement needs a check")
        if status != "automated" and (
            checks
            or not isinstance(requirement["reason"], str)
            or not requirement["reason"].strip()
        ):
            raise ValueError(f"{name}: nonautomated requirement needs a reason and no checks")
        if any(check not in check_ids for check in checks):
            raise ValueError(f"{name}: unknown check reference")
        requirement_ids.add(name)
        referenced_checks.update(checks)
        requirements.append(requirement)
    if referenced_checks != check_ids:
        raise ValueError("every check must belong to at least one requirement")
    return requirements


def failed_finding(code: str, name: str, message: str) -> dict:
    return {
        "severity": "error",
        "code": code,
        "record_id": name,
        "message": message,
    }


def requirement_links_valid(
    root: Path, requirement: dict, claim_ids: set[str], findings: list[dict]
) -> bool:
    valid = True
    for artifact in requirement["artifacts"]:
        try:
            project_file(root, artifact)
        except (ValueError, OSError, RecursionError) as exc:
            findings.append(
                failed_finding(
                    "integrity-check-failed",
                    requirement["id"],
                    f"requirement artifact: {exc}",
                )
            )
            valid = False
    unknown_claims = sorted(set(requirement["claims"]) - claim_ids)
    if unknown_claims:
        findings.append(
            failed_finding(
                "integrity-unknown-claim",
                requirement["id"],
                f"unknown current claims: {', '.join(unknown_claims)}",
            )
        )
        valid = False
    return valid


def check_contract(
    root: Path, path: Path, claim_ids: set[str]
) -> tuple[dict, list[dict]]:
    report = {"path": str(path), "sha256": None, "passed": []}
    findings = []
    try:
        raw = path.read_bytes()
        report["sha256"] = hashlib.sha256(raw).hexdigest()
        spec = parse_json(raw)
        version = spec.get("version") if isinstance(spec, dict) else None
        expected = {"version", "checks"}
        fields(spec, expected | {"requirements"} if version == "2" else expected)
        if (
            version not in {"1", "2"}
            or not isinstance(spec["checks"], list)
            or not spec["checks"]
        ):
            raise ValueError("expected version '1' or '2' and nonempty checks array")
        ids = set()
        for rule in spec["checks"]:
            name = rule.get("id") if isinstance(rule, dict) else None
            if not isinstance(name, str) or not name.strip() or name in ids:
                raise ValueError("expected unique nonempty check ID")
            ids.add(name)
        requirements = validate_requirements(spec, ids) if version == "2" else []
        if requirements:
            report["coverage"] = {
                "passed": [],
                "failed": [],
                "manual": [],
                "not_assessed": [],
            }
        for rule in spec["checks"]:
            name = rule["id"]
            try:
                check_one(root, rule)
            except (ValueError, OSError, RecursionError) as exc:
                findings.append(
                    failed_finding("integrity-check-failed", name, str(exc))
                )
            else:
                report["passed"].append(name)
        passed = set(report["passed"])
        for requirement in requirements:
            name = requirement["id"]
            links_valid = requirement_links_valid(root, requirement, claim_ids, findings)
            status = requirement.get("status", "automated")
            if status == "not_assessed":
                report["coverage"]["not_assessed"].append(name)
                findings.append(
                    failed_finding(
                        "integrity-requirement-not-assessed",
                        name,
                        requirement["reason"],
                    )
                )
            elif status == "manual":
                key = "manual" if links_valid else "failed"
                report["coverage"][key].append(name)
            else:
                checks_passed = all(check in passed for check in requirement["checks"])
                key = "passed" if links_valid and checks_passed else "failed"
                report["coverage"][key].append(name)
    except (ValueError, TypeError, OSError, RecursionError) as exc:
        findings.append(
            {
                "severity": "error",
                "code": "invalid-integrity-contract",
                "message": str(exc),
            }
        )
    return report, findings
