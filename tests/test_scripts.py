"""End-to-end tests for the dossier scripts.

Every test drives the scripts through their command-line interface against a
throwaway project directory, mirroring how an agent uses them.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
START = "2026-08-14T01:00:00Z"
END = "2026-08-14T01:30:00Z"


def run_script(name: str, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def append_record(project: Path, ledger: str, record: dict) -> None:
    with (project / ".research" / ledger).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def make_claim(claim_id: str, **overrides: object) -> dict:
    record = {
        "id": claim_id,
        "text": "test claim",
        "claim_type": "empirical",
        "lifecycle_state": "proposed",
        "evidential_status": "not_assessed",
        "evidence_ids": [],
        "run_ids": [],
        "artifact_paths": [],
        "caveats": [],
        "scope": "test",
        "updated_at": "2026-08-14",
    }
    record.update(overrides)
    return record


def make_evidence(source_id: str, **overrides: object) -> dict:
    record = {
        "id": source_id,
        "title": "test source",
        "url": "https://example.org/paper",
        "accessed_at": "2026-08-14",
        "verification": "full-text-checked",
        "locator": "Sec. 1",
        "supports": [],
        "challenges": [],
        "contextualizes": [],
    }
    record.update(overrides)
    return record


@pytest.fixture
def project(tmp_path: Path) -> Path:
    result = run_script("research_state.py", "init", "--title", "Test", "--owner", "tester", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    return tmp_path


@pytest.fixture
def project_with_run(project: Path) -> Path:
    (project / "cfg.yaml").write_text("option: 1\n", encoding="utf-8")
    (project / "out.txt").write_text("output data\n", encoding="utf-8")
    result = capture(project, "RUN-001")
    assert result.returncode == 0, result.stderr
    return project


def capture(project: Path, run_id: str, *extra: str, **kwargs: str) -> subprocess.CompletedProcess[str]:
    args = [
        "--run-id",
        run_id,
        "--experiment-id",
        "EXP-001",
        "--operator",
        "tester",
        "--started-at",
        kwargs.get("started_at", START),
        "--ended-at",
        kwargs.get("ended_at", END),
        "--phase",
        kwargs.get("phase", "full"),
        "--status",
        kwargs.get("status", "completed"),
        "--result-kind",
        kwargs.get("result_kind", "measured"),
        "--command",
        "python train.py",
        "--config",
        "cfg.yaml",
        "--output",
        "out.txt",
        *extra,
    ]
    return run_script("capture_run.py", *args, cwd=project)


def audit(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_script("audit_research.py", "--json", *args, cwd=project)


def audit_report(project: Path, *args: str) -> tuple[int, dict]:
    result = audit(project, *args)
    return result.returncode, json.loads(result.stdout)


def finding_codes(report: dict) -> set[str]:
    return {item["code"] for item in report["findings"]}


class TestResearchState:
    def test_init_validate_status(self, project: Path) -> None:
        assert (project / ".research" / "state.json").is_file()
        assert run_script("research_state.py", "validate", cwd=project).returncode == 0
        result = run_script("research_state.py", "status", cwd=project)
        assert result.returncode == 0
        summary = json.loads(result.stdout)
        assert summary["stage"] == "scoping"
        assert summary["record_counts"] == {"evidence": 0, "claims": 0, "experiments": 0}

    def test_init_refuses_existing_dossier(self, project: Path) -> None:
        result = run_script("research_state.py", "init", "--title", "X", "--owner", "y", cwd=project)
        assert result.returncode == 2

    def test_transition(self, project: Path) -> None:
        result = run_script(
            "research_state.py",
            "transition",
            "--stage",
            "design",
            "--status",
            "planned",
            "--reason",
            "design frozen",
            "--evidence",
            "plan.md",
            "--alternative",
            "stay in scoping",
            "--consequence",
            "implementation may start",
            "--owner",
            "tester",
            "--revisit-condition",
            "design change",
            cwd=project,
        )
        assert result.returncode == 0, result.stderr
        state = json.loads((project / ".research" / "state.json").read_text(encoding="utf-8"))
        assert (state["stage"], state["stage_status"]) == ("design", "planned")
        assert len(state["decision_index"]) == 2

    def test_update_replaces_lists_and_clears_scalars(self, project: Path) -> None:
        first = run_script(
            "research_state.py",
            "update",
            "--contribution-type",
            "empirical finding",
            "--next-action",
            "a",
            "--next-action",
            "b",
            cwd=project,
        )
        assert first.returncode == 0, first.stderr
        second = run_script(
            "research_state.py",
            "update",
            "--contribution-type",
            "",
            "--next-action",
            "c",
            cwd=project,
        )
        assert second.returncode == 0, second.stderr
        state = json.loads((project / ".research" / "state.json").read_text(encoding="utf-8"))
        assert state["contribution_type"] is None
        assert state["next_actions"] == ["c"]

    def test_update_requires_options(self, project: Path) -> None:
        assert run_script("research_state.py", "update", cwd=project).returncode == 2


class TestCaptureRun:
    def test_capture_and_clean_audit(self, project_with_run: Path) -> None:
        manifest_path = project_with_run / ".research" / "runs" / "RUN-001" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["schema_version"] == "1.1"
        assert manifest["evidence_eligibility"] == "candidate_pending_verification"
        assert "capture_environment" in manifest
        code, report = audit_report(project_with_run)
        assert code == 0, report
        assert report["counts"] == {"error": 0, "warning": 0}

    def test_duplicate_run_id_rejected(self, project_with_run: Path) -> None:
        result = capture(project_with_run, "RUN-001")
        assert result.returncode == 2
        assert "already recorded" in result.stderr

    def test_failed_run_requires_reason(self, project: Path) -> None:
        (project / "cfg.yaml").write_text("option: 1\n", encoding="utf-8")
        (project / "out.txt").write_text("output data\n", encoding="utf-8")
        result = capture(project, "RUN-002", status="failed")
        assert result.returncode == 2
        assert "failure-reason" in result.stderr

    def test_large_file_requires_immutable_version(self, project: Path) -> None:
        (project / "cfg.yaml").write_text("option: 1\n", encoding="utf-8")
        big = project / "out.txt"
        with big.open("wb") as handle:
            handle.truncate(64 * 1024 * 1024 + 1)
        rejected = capture(project, "RUN-003")
        assert rejected.returncode == 2
        assert "--file-version" in rejected.stderr
        accepted = capture(project, "RUN-003", "--file-version", "out.txt=dataset-v1")
        assert accepted.returncode == 0, accepted.stderr

    def test_tampered_output_detected(self, project_with_run: Path) -> None:
        (project_with_run / "out.txt").write_text("altered after capture\n", encoding="utf-8")
        code, report = audit_report(project_with_run)
        assert code == 1
        assert {"recorded-outputs-size-changed", "recorded-outputs-hash-changed"} & finding_codes(report)


class TestAudit:
    def test_non_independent_verification_flagged(self, project_with_run: Path) -> None:
        append_record(
            project_with_run,
            "claims.jsonl",
            make_claim(
                "CLM-001",
                lifecycle_state="verified",
                evidential_status="supported",
                run_ids=["RUN-001"],
                verification_run_ids=["RUN-001"],
                artifact_paths=["out.txt"],
            ),
        )
        code, report = audit_report(project_with_run)
        assert code == 1
        assert "verification-run-not-independent" in finding_codes(report)

    def test_superseded_claim_is_not_audited(self, project_with_run: Path) -> None:
        append_record(
            project_with_run,
            "claims.jsonl",
            make_claim(
                "CLM-001",
                lifecycle_state="verified",
                evidential_status="supported",
                run_ids=["RUN-001"],
                verification_run_ids=["RUN-001"],
                artifact_paths=["out.txt"],
            ),
        )
        append_record(
            project_with_run,
            "claims.jsonl",
            make_claim(
                "CLM-002",
                supersedes="CLM-001",
                lifecycle_state="analyzed",
                evidential_status="supported",
                run_ids=["RUN-001"],
                artifact_paths=["out.txt"],
            ),
        )
        code, report = audit_report(project_with_run)
        assert code == 0, report
        assert report["counts"]["error"] == 0

    def test_claim_linking_superseded_evidence_warns(self, project: Path) -> None:
        append_record(project, "evidence.jsonl", make_evidence("SRC-001", supports=["CLM-001"]))
        append_record(
            project,
            "evidence.jsonl",
            make_evidence("SRC-002", supersedes="SRC-001", supports=["CLM-001"]),
        )
        append_record(
            project,
            "claims.jsonl",
            make_claim("CLM-001", claim_type="contextual", evidence_ids=["SRC-001", "SRC-002"]),
        )
        code, report = audit_report(project)
        assert code == 0, report
        assert "claim-links-superseded-evidence" in finding_codes(report)

    def test_metadata_only_evidence_rejected(self, project: Path) -> None:
        append_record(
            project,
            "evidence.jsonl",
            make_evidence("SRC-001", verification="metadata-only", locator=None, supports=["CLM-001"]),
        )
        append_record(
            project,
            "claims.jsonl",
            make_claim("CLM-001", claim_type="contextual", evidence_ids=["SRC-001"]),
        )
        code, report = audit_report(project)
        assert code == 1
        codes = finding_codes(report)
        assert "metadata-used-substantively" in codes
        assert "claim-uses-metadata-as-evidence" in codes

    def test_reported_claim_artifact_autoscanned_for_placeholders(self, project: Path) -> None:
        (project / "paper.md").write_text("Result: [RESULT PENDING]\n", encoding="utf-8")
        append_record(
            project,
            "claims.jsonl",
            make_claim(
                "CLM-001",
                claim_type="contextual",
                lifecycle_state="reported",
                evidential_status="supported",
                artifact_paths=["paper.md"],
            ),
        )
        code, report = audit_report(project)
        assert code == 1
        assert "unresolved-placeholder" in finding_codes(report)

    def test_explicit_scan_still_reports_placeholders(self, project: Path) -> None:
        (project / "draft.md").write_text("[CITATION NEEDED]\n", encoding="utf-8")
        code, report = audit_report(project, "--scan", "draft.md")
        assert code == 1
        assert "unresolved-placeholder" in finding_codes(report)
