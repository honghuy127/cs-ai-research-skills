"""End-to-end tests for the dossier scripts.

Every test drives the scripts through their command-line interface against a
throwaway project directory, mirroring how an agent uses them.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import zipfile
import zlib
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
START = "2026-08-14T01:00:00Z"
END = "2026-08-14T01:30:00Z"


def run_script(
    name: str, *args: str, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=cwd,
        env=env,
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

    @pytest.mark.parametrize(("title", "owner"), [(" ", "tester"), ("Test", " ")])
    def test_init_rejects_blank_identity(self, tmp_path: Path, title: str, owner: str) -> None:
        result = run_script(
            "research_state.py", "init", "--title", title, "--owner", owner, cwd=tmp_path
        )
        assert result.returncode == 2
        assert "must be non-empty" in result.stderr

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

    def test_update_records_operating_mode_and_status_reports_it(self, project: Path) -> None:
        result = run_script("research_state.py", "update", "--operating-mode", "human-led", cwd=project)
        assert result.returncode == 0, result.stderr
        state = json.loads((project / ".research" / "state.json").read_text(encoding="utf-8"))
        assert state["constraints"]["operating_mode"] == "human-led"
        status = run_script("research_state.py", "status", cwd=project)
        assert json.loads(status.stdout)["operating_mode"] == "human-led"

    def test_update_rejects_unknown_operating_mode(self, project: Path) -> None:
        result = run_script("research_state.py", "update", "--operating-mode", "autopilot", cwd=project)
        assert result.returncode == 2

    def test_validate_rejects_invalid_operating_mode(self, project: Path) -> None:
        state_path = project / ".research" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["constraints"]["operating_mode"] = "autopilot"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        result = run_script("research_state.py", "validate", cwd=project)
        assert result.returncode == 1
        assert "invalid constraints.operating_mode" in result.stdout

    def test_decide_appends_decision_without_stage_change(self, project: Path) -> None:
        result = run_script(
            "research_state.py",
            "decide",
            "--decision",
            "keep the three-seed design",
            "--reason",
            "compute budget",
            "--evidence",
            "advisory: design gate would be CONDITIONAL",
            "--alternative",
            "five seeds",
            "--consequence",
            "wider intervals on CLM-002",
            "--owner",
            "tester",
            "--revisit-condition",
            "more compute",
            cwd=project,
        )
        assert result.returncode == 0, result.stderr
        decision_id = result.stdout.strip()
        assert decision_id.startswith("DEC-")
        state = json.loads((project / ".research" / "state.json").read_text(encoding="utf-8"))
        assert (state["stage"], state["stage_status"]) == ("scoping", "proposed")
        assert [entry["id"] for entry in state["decision_index"]][-1] == decision_id
        assert state["decision_index"][-1]["summary"] == "keep the three-seed design"
        log = (project / ".research" / "decisions.md").read_text(encoding="utf-8")
        assert f"## {decision_id}: keep the three-seed design" in log
        assert "advisory: design gate would be CONDITIONAL" in log
        assert run_script("research_state.py", "validate", cwd=project).returncode == 0

    @pytest.mark.parametrize("blank_option", ["--decision", "--reason", "--evidence", "--owner"])
    def test_decide_rejects_blank_fields(self, project: Path, blank_option: str) -> None:
        values = {
            "--decision": "override",
            "--reason": "why",
            "--evidence": "advisory",
            "--alternative": "comply",
            "--consequence": "none",
            "--owner": "tester",
            "--revisit-condition": "never",
        }
        values[blank_option] = " "
        args = [item for pair in values.items() for item in pair]
        result = run_script("research_state.py", "decide", *args, cwd=project)
        assert result.returncode == 2
        assert "non-empty" in result.stderr
        state = json.loads((project / ".research" / "state.json").read_text(encoding="utf-8"))
        assert len(state["decision_index"]) == 1

    def test_update_rejects_blank_list_items(self, project: Path) -> None:
        result = run_script("research_state.py", "update", "--next-action", "  ", cwd=project)
        assert result.returncode == 2
        assert "non-empty" in result.stderr

    def test_transition_rejects_blank_fields(self, project: Path) -> None:
        result = run_script(
            "research_state.py",
            "transition",
            "--stage",
            "design",
            "--status",
            "planned",
            "--reason",
            " ",
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
        assert result.returncode == 2
        assert "non-empty" in result.stderr

    def test_transition_rejects_noop(self, project: Path) -> None:
        result = run_script(
            "research_state.py",
            "transition",
            "--stage",
            "scoping",
            "--status",
            "proposed",
            "--reason",
            "restate position",
            "--evidence",
            "none",
            "--alternative",
            "none",
            "--consequence",
            "none",
            "--owner",
            "tester",
            "--revisit-condition",
            "none",
            cwd=project,
        )
        assert result.returncode == 2
        assert "already at" in result.stderr

    def test_validate_rejects_bad_timestamp(self, project: Path) -> None:
        state_path = project / ".research" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["updated_at"] = "yesterday"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        result = run_script("research_state.py", "validate", cwd=project)
        assert result.returncode == 1
        assert "invalid ISO 8601 updated_at" in result.stdout

    def test_validate_rejects_non_object_state(self, project: Path) -> None:
        (project / ".research" / "state.json").write_text("[]\n", encoding="utf-8")
        result = run_script("research_state.py", "validate", cwd=project)
        assert result.returncode == 1
        assert "expected JSON object" in result.stdout

    def test_validate_reports_non_utf8_state_and_ledger(self, project: Path) -> None:
        state_path = project / ".research" / "state.json"
        original_state = state_path.read_bytes()
        state_path.write_bytes(b"\xff")
        state_result = run_script("research_state.py", "validate", cwd=project)
        assert state_result.returncode == 1
        assert "cannot read JSON" in state_result.stdout
        assert "Traceback" not in state_result.stderr

        state_path.write_bytes(original_state)
        (project / ".research" / "claims.jsonl").write_bytes(b"\xff")
        ledger_result = run_script("research_state.py", "validate", cwd=project)
        assert ledger_result.returncode == 1
        assert "cannot read ledger" in ledger_result.stdout
        assert "Traceback" not in ledger_result.stderr
        audit_code, audit_data = audit_report(project)
        assert audit_code == 1
        assert "unreadable-ledger" in finding_codes(audit_data)

    def test_validate_rejects_duplicate_decision_ids(self, project: Path) -> None:
        state_path = project / ".research" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["decision_index"].append(dict(state["decision_index"][0]))
        state_path.write_text(json.dumps(state), encoding="utf-8")
        result = run_script("research_state.py", "validate", cwd=project)
        assert result.returncode == 1
        assert "duplicate decision ID" in result.stdout

    def test_validate_rejects_reversed_run_times(self, project: Path) -> None:
        append_record(
            project,
            "experiments.jsonl",
            {
                "run_id": "RUN-001",
                "experiment_id": "EXP-001",
                "manifest_path": ".research/runs/RUN-001/manifest.json",
                "phase": "full",
                "status": "completed",
                "result_kind": "measured",
                "evidence_eligibility": "candidate_pending_verification",
                "started_at": END,
                "ended_at": START,
                "recorded_at": START,
            },
        )
        result = run_script("research_state.py", "validate", cwd=project)
        assert result.returncode == 1
        assert "ended_at precedes started_at" in result.stdout

    def test_validate_requires_offsets_for_run_timestamps(self, project: Path) -> None:
        append_record(
            project,
            "experiments.jsonl",
            {
                "run_id": "RUN-001",
                "experiment_id": "EXP-001",
                "manifest_path": ".research/runs/RUN-001/manifest.json",
                "phase": "full",
                "status": "completed",
                "result_kind": "measured",
                "evidence_eligibility": "candidate_pending_verification",
                "started_at": "2026-08-14T01:00:00",
                "ended_at": "2026-08-14T01:30:00",
                "recorded_at": "2026-08-14T01:31:00",
            },
        )
        result = run_script("research_state.py", "validate", cwd=project)
        assert result.returncode == 1
        assert "must include a UTC offset or Z" in result.stdout


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

    def test_blank_command_rejected(self, project: Path) -> None:
        (project / "cfg.yaml").write_text("option: 1\n", encoding="utf-8")
        (project / "out.txt").write_text("output data\n", encoding="utf-8")
        result = capture(project, "RUN-002", "--command", "  ")
        assert result.returncode == 2
        assert "command must be non-empty" in result.stderr

    def test_capture_without_git_executable_records_unavailable(self, project: Path) -> None:
        (project / "cfg.yaml").write_text("option: 1\n", encoding="utf-8")
        (project / "out.txt").write_text("output data\n", encoding="utf-8")
        env = dict(os.environ)
        env["PATH"] = ""
        result = run_script(
            "capture_run.py",
            "--run-id",
            "RUN-002",
            "--experiment-id",
            "EXP-001",
            "--operator",
            "tester",
            "--started-at",
            START,
            "--ended-at",
            END,
            "--phase",
            "full",
            "--status",
            "completed",
            "--result-kind",
            "measured",
            "--command",
            "python train.py",
            "--config",
            "cfg.yaml",
            "--output",
            "out.txt",
            cwd=project,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        manifest = json.loads(
            (project / ".research" / "runs" / "RUN-002" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        assert manifest["git"]["available"] is False
        assert manifest["git"]["reason"]

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

    def test_file_version_id_may_contain_equals(self, project: Path) -> None:
        (project / "cfg.yaml").write_text("option: 1\n", encoding="utf-8")
        big = project / "out.txt"
        with big.open("wb") as handle:
            handle.truncate(64 * 1024 * 1024 + 1)
        result = capture(project, "RUN-004", "--file-version", "out.txt=sha256=abc==")
        assert result.returncode == 0, result.stderr
        manifest = json.loads(
            (project / ".research" / "runs" / "RUN-004" / "manifest.json").read_text(encoding="utf-8")
        )
        assert manifest["outputs"][0]["external_version"] == "sha256=abc=="

    def test_dirty_snapshot_covers_repo_subdirectory_root(self, tmp_path: Path) -> None:
        if shutil.which("git") is None:
            pytest.skip("git is unavailable")
        repo = tmp_path / "repo"
        sub = repo / "sub"
        sub.mkdir(parents=True)

        def git(*parts: str) -> None:
            subprocess.run(
                ["git", "-c", "user.email=t@example.org", "-c", "user.name=T", *parts],
                cwd=repo,
                check=True,
                capture_output=True,
            )

        git("init", "-q")
        (sub / "inner.txt").write_text("clean\n", encoding="utf-8")
        (repo / "outer.txt").write_text("clean\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-q", "-m", "init")
        init = run_script("research_state.py", "init", "--title", "T", "--owner", "t", cwd=sub)
        assert init.returncode == 0, init.stderr
        (sub / "inner.txt").write_text("dirty\n", encoding="utf-8")
        (sub / "cfg.yaml").write_text("option: 1\n", encoding="utf-8")
        (sub / "out.txt").write_text("output\n", encoding="utf-8")
        result = capture(sub, "RUN-001")
        assert result.returncode == 0, result.stderr
        manifest = json.loads(
            (sub / ".research" / "runs" / "RUN-001" / "manifest.json").read_text(encoding="utf-8")
        )
        dirty = {record["path"]: record for record in manifest["git"]["dirty_file_hashes"]}
        assert dirty["inner.txt"]["kind"] == "file"
        assert dirty["inner.txt"]["sha256"]
        assert "sub/inner.txt" not in dirty
        assert "outer.txt" not in dirty
        code, report = audit_report(sub)
        assert code == 0, report

    def test_os_junk_file_in_runs_tolerated(self, project_with_run: Path) -> None:
        (project_with_run / ".research" / "runs" / ".DS_Store").write_bytes(b"\x00")
        result = capture(project_with_run, "RUN-002")
        assert result.returncode == 0, result.stderr
        code, report = audit_report(project_with_run)
        assert code == 0, report
        assert "junk-file-in-runs" in finding_codes(report)

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

    def test_metadata_only_contextualizes_without_backlink(self, project: Path) -> None:
        append_record(
            project,
            "evidence.jsonl",
            make_evidence(
                "SRC-001", verification="metadata-only", locator=None, supports=[], contextualizes=["CLM-001"]
            ),
        )
        append_record(project, "claims.jsonl", make_claim("CLM-001", claim_type="contextual", evidence_ids=[]))
        code, report = audit_report(project)
        assert code == 0, report
        assert report["counts"]["error"] == 0

    def test_metadata_only_contextualize_may_be_linked(self, project: Path) -> None:
        append_record(
            project,
            "evidence.jsonl",
            make_evidence(
                "SRC-001", verification="metadata-only", locator=None, contextualizes=["CLM-001"]
            ),
        )
        append_record(
            project,
            "claims.jsonl",
            make_claim("CLM-001", claim_type="contextual", evidence_ids=["SRC-001"]),
        )
        code, report = audit_report(project)
        assert code == 0, report
        assert "claim-uses-metadata-as-evidence" not in finding_codes(report)

    def test_superseded_run_record_is_not_audited(self, project_with_run: Path) -> None:
        result = capture(project_with_run, "RUN-002")
        assert result.returncode == 0, result.stderr
        ledger = project_with_run / ".research" / "experiments.jsonl"
        records = [
            json.loads(line)
            for line in ledger.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        records[0]["phase"] = "pilot"  # now contradicts its manifest
        records[1]["supersedes"] = "RUN-001"
        ledger.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        append_record(
            project_with_run,
            "claims.jsonl",
            make_claim(
                "CLM-001", claim_type="contextual", run_ids=["RUN-001"], artifact_paths=["out.txt"]
            ),
        )
        code, report = audit_report(project_with_run)
        assert code == 0, report
        assert "ledger-manifest-mismatch" not in finding_codes(report)
        assert "claim-links-superseded-run" in finding_codes(report)

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

    def test_source_only_dossier_audits_clean_with_no_runs(self, project: Path) -> None:
        append_record(project, "evidence.jsonl", make_evidence("SRC-001", supports=["CLM-001"]))
        append_record(
            project,
            "claims.jsonl",
            make_claim(
                "CLM-001",
                claim_type="descriptive",
                lifecycle_state="verified",
                evidential_status="supported",
                evidence_ids=["SRC-001"],
            ),
        )
        code, report = audit_report(project)
        assert code == 0, report
        assert report["counts"]["error"] == 0

    def test_empirical_claim_still_requires_a_run(self, project: Path) -> None:
        append_record(project, "evidence.jsonl", make_evidence("SRC-001", supports=["CLM-001"]))
        append_record(
            project,
            "claims.jsonl",
            make_claim(
                "CLM-001",
                claim_type="empirical",
                lifecycle_state="verified",
                evidential_status="supported",
                evidence_ids=["SRC-001"],
            ),
        )
        code, report = audit_report(project)
        assert code == 1
        codes = finding_codes(report)
        assert "empirical-claim-without-run" in codes
        assert "verified-claim-without-independent-check" in codes

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


VALID_DRAWIO = """<mxfile host="app.diagrams.net">
  <diagram id="p1" name="method">
    <mxGraphModel page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="a" value="Encoder" style="rounded=1;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="120" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="b" value="Decoder" style="rounded=1;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="240" y="40" width="120" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="e" value="latents" style="edgeStyle=orthogonalEdgeStyle;fontSize=10;" edge="1" parent="1" source="a" target="b">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


def drawio_report(project: Path, *args: str) -> tuple[int, dict]:
    result = run_script("validate_drawio.py", *args, cwd=project)
    return result.returncode, json.loads(result.stdout)


def compressed_drawio(model: str) -> str:
    payload = base64.b64encode(zlib.compress(urllib.parse.quote(model, safe="").encode("utf-8"), 9)[2:-4]).decode("ascii")
    return f'<mxfile><diagram id="p1" name="compressed">{payload}</diagram></mxfile>'


class TestValidateDrawio:
    def test_valid_diagram_passes(self, tmp_path: Path) -> None:
        (tmp_path / "fig.drawio").write_text(VALID_DRAWIO, encoding="utf-8")
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 0, report
        entry = report["reports"][0]
        assert entry["status"] == "pass"
        assert entry["pages"][0]["vertices"] == 2
        assert entry["pages"][0]["edges"] == 1

    def test_compressed_diagram_decodes(self, tmp_path: Path) -> None:
        model = (
            '<mxGraphModel page="1" pageWidth="850" pageHeight="1100"><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>'
            '<mxCell id="n" value="Node" style="fontSize=12;" vertex="1" parent="1">'
            '<mxGeometry x="10" y="10" width="80" height="30" as="geometry"/></mxCell>'
            "</root></mxGraphModel>"
        )
        (tmp_path / "fig.drawio").write_text(compressed_drawio(model), encoding="utf-8")
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 0, report
        assert report["reports"][0]["pages"][0]["vertices"] == 1

    def test_compressed_diagram_expansion_is_bounded(self, tmp_path: Path) -> None:
        (tmp_path / "fig.drawio").write_text(
            compressed_drawio("x" * (8 * 1024 * 1024 + 1)), encoding="utf-8"
        )
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 1
        errors = report["reports"][0]["errors"]
        assert {finding["code"] for finding in errors} == {"decode-error", "no-pages"}
        assert "safety limit" in errors[0]["message"]

    def test_dangling_edge_and_parent_fail(self, tmp_path: Path) -> None:
        broken = VALID_DRAWIO.replace('target="b"', 'target="ghost"').replace('parent="1">\n          <mxGeometry x="240"', 'parent="nowhere">\n          <mxGeometry x="240"')
        (tmp_path / "fig.drawio").write_text(broken, encoding="utf-8")
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 1
        codes = {finding["code"] for finding in report["reports"][0]["errors"]}
        assert "dangling-edge" in codes
        assert "dangling-parent" in codes

    def test_warnings_pass_normally_but_fail_strict(self, tmp_path: Path) -> None:
        draft = VALID_DRAWIO.replace('value="Encoder"', 'value="[RESULT PENDING]"').replace("fontSize=12;", "fontSize=5;")
        (tmp_path / "fig.drawio").write_text(draft, encoding="utf-8")
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 0
        assert report["reports"][0]["status"] == "pass-with-warnings"
        codes = {finding["code"] for finding in report["reports"][0]["warnings"]}
        assert "placeholder-label" in codes
        assert "small-font" in codes
        strict, strict_report = drawio_report(tmp_path, "--json", "--strict", "fig.drawio")
        assert strict == 1
        assert strict_report["reports"][0]["status"] == "fail"

    def test_embedded_raster_warns(self, tmp_path: Path) -> None:
        raster = VALID_DRAWIO.replace(
            'style="rounded=1;fontSize=12;" vertex="1" parent="1">\n          <mxGeometry x="240"',
            'style="shape=image;imageAspect=0;image=data:image/png;base64,iVBORw0KGg;fontSize=12;" vertex="1" parent="1">\n          <mxGeometry x="240"',
        )
        (tmp_path / "fig.drawio").write_text(raster, encoding="utf-8")
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 0, report
        codes = {finding["code"] for finding in report["reports"][0]["warnings"]}
        assert "embedded-raster" in codes

    def test_unlabeled_image_vertex_is_not_flagged(self, tmp_path: Path) -> None:
        image = VALID_DRAWIO.replace(
            'value="Decoder" style="rounded=1;fontSize=12;"',
            'value="" style="image;html=1;image=data:image/svg+xml,PHN2Zz48L3N2Zz4=;"',
        )
        (tmp_path / "fig.drawio").write_text(image, encoding="utf-8")
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 0, report
        codes = {finding["code"] for finding in report["reports"][0]["warnings"]}
        assert "empty-label" not in codes

    def test_malformed_xml_fails(self, tmp_path: Path) -> None:
        (tmp_path / "fig.drawio").write_text("<mxfile><diagram>", encoding="utf-8")
        code, report = drawio_report(tmp_path, "--json", "fig.drawio")
        assert code == 1
        codes = {finding["code"] for finding in report["reports"][0]["errors"]}
        assert "parse-error" in codes


CLEAN_LATEX_LOG = r"""This is pdfTeX, Version 3.141592653-2.6-1.40.26 (TeX Live 2024)
(./main.tex [1] [2]
Underfull \hbox (badness 10000) in paragraph at lines 30--35
(./main.aux)
Output written on main.pdf (2 pages, 34567 bytes).
"""

WARN_LATEX_LOG = r"""This is pdfTeX, Version 3.141592653-2.6-1.40.26 (TeX Live 2024)
(./main.tex [1]
Overfull \hbox (15.57pt too wide) in paragraph at lines 123--124
[]\T1/lmr/m/n/10 Some very long unbreakable-identifier overflows here
LaTeX Warning: Reference `fig:missing' on page 2 undefined on input line 55.
[2] [3]
LaTeX Warning: Citation `smith2020' undefined on input line 88.
(./main.aux)
LaTeX Warning: There were undefined references.
Output written on main.pdf (3 pages, 123456 bytes).
"""

ERROR_LATEX_LOG = r"""This is pdfTeX, Version 3.141592653-2.6-1.40.26 (TeX Live 2024)
(./main.tex
! Undefined control sequence.
l.42 \badcommand

?
[1]
Output written on main.pdf (1 page, 1234 bytes).
"""


def latex_log_report(project: Path, *args: str) -> tuple[int, dict]:
    result = run_script("check_latex_log.py", *args, cwd=project)
    return result.returncode, json.loads(result.stdout)


class TestCheckLatexLog:
    def test_clean_log_passes_and_reports_page_count(self, tmp_path: Path) -> None:
        (tmp_path / "main.log").write_text(CLEAN_LATEX_LOG, encoding="utf-8")
        code, report = latex_log_report(tmp_path, "--json", "main.log")
        assert code == 0, report
        assert report["status"] == "pass"
        assert report["pages"] == 2
        assert report["output_pdf"] == "main.pdf"
        assert report["errors"] == []
        assert report["warnings"] == []
        assert {finding["code"] for finding in report["info"]} == {"underfull-box"}

    def test_warning_log_passes_normally_but_fails_strict(self, tmp_path: Path) -> None:
        (tmp_path / "main.log").write_text(WARN_LATEX_LOG, encoding="utf-8")
        code, report = latex_log_report(tmp_path, "--json", "main.log")
        assert code == 0, report
        assert report["status"] == "pass-with-warnings"
        codes = {finding["code"] for finding in report["warnings"]}
        assert {"overfull-box", "undefined-reference", "undefined-citation"} <= codes
        strict_code, strict_report = latex_log_report(tmp_path, "--json", "--strict", "main.log")
        assert strict_code == 1
        assert strict_report["status"] == "fail"

    def test_error_log_fails(self, tmp_path: Path) -> None:
        (tmp_path / "main.log").write_text(ERROR_LATEX_LOG, encoding="utf-8")
        code, report = latex_log_report(tmp_path, "--json", "main.log")
        assert code == 1
        assert report["status"] == "fail"
        error = report["errors"][0]
        assert error["code"] == "latex-error"
        assert "source line 42" in error["message"]

    def test_pdftex_error_without_space_detected(self, tmp_path: Path) -> None:
        log = CLEAN_LATEX_LOG.replace(
            "(./main.aux)",
            "(./main.aux)\n!pdfTeX error (font expansion): auto expansion is only"
            " possible with scalable fonts.",
        )
        (tmp_path / "main.log").write_text(log, encoding="utf-8")
        code, report = latex_log_report(tmp_path, "--json", "main.log")
        assert code == 1
        assert "latex-error" in {finding["code"] for finding in report["errors"]}

    def test_max_pages_enforced(self, tmp_path: Path) -> None:
        (tmp_path / "main.log").write_text(WARN_LATEX_LOG, encoding="utf-8")
        code, report = latex_log_report(tmp_path, "--json", "--max-pages", "2", "main.log")
        assert code == 1
        assert {finding["code"] for finding in report["errors"]} == {"page-limit-exceeded"}
        ok_code, ok_report = latex_log_report(tmp_path, "--json", "--max-pages", "3", "main.log")
        assert ok_code == 0
        assert ok_report["errors"] == []

    def test_unreadable_log_fails(self, tmp_path: Path) -> None:
        code, report = latex_log_report(tmp_path, "--json", "missing.log")
        assert code == 1
        assert {finding["code"] for finding in report["errors"]} == {"unreadable-log"}


OOXML_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Default Extension="png" ContentType="image/png"/>'
    '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
    '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
    '<Override PartName="/ppt/slides/slide2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
    "</Types>"
)

OOXML_ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
    "</Relationships>"
)

PPTX_PRESENTATION = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '<p:sldIdLst><p:sldId id="256" r:id="rId2"/><p:sldId id="257" r:id="rId3"/></p:sldIdLst>'
    "</p:presentation>"
)


def pptx_slide(text: str, show: str = "1") -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" show="' + show + '">'
        "<p:cSld><p:spTree><p:sp><a:t>" + text + "</a:t></p:sp></p:spTree></p:cSld></p:sld>"
    )


PPTX_SLIDE_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/>'
    "</Relationships>"
)

DOCX_DOCUMENT = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body>"
    "<w:p><w:r><w:t>First paragraph.</w:t></w:r></w:p>"
    "<w:p><w:r><w:t>Second paragraph.</w:t></w:r></w:p>"
    "</w:body></w:document>"
)

XLSX_WORKBOOK = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<sheets><sheet name="Data" sheetId="1"/></sheets>'
    "</workbook>"
)

XLSX_SHEET = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    "<sheetData><row>"
    '<c t="inlineStr"><is><t>[EVIDENCE NEEDED]</t></is></c>'
    "</row></sheetData></worksheet>"
)

DOCX_CORE_PROPS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/">'
    "<dc:creator>Jane Doe</dc:creator>"
    "</cp:coreProperties>"
)


def base_pptx_parts() -> dict[str, str | bytes]:
    return {
        "[Content_Types].xml": OOXML_CONTENT_TYPES,
        "_rels/.rels": OOXML_ROOT_RELS,
        "ppt/presentation.xml": PPTX_PRESENTATION,
        "ppt/slides/slide1.xml": pptx_slide("Title slide"),
        "ppt/slides/_rels/slide1.xml.rels": PPTX_SLIDE_RELS,
        "ppt/slides/slide2.xml": pptx_slide("Result: 0.62 accuracy"),
        "ppt/media/image1.png": b"\x89PNG fake",
        "docProps/core.xml": DOCX_CORE_PROPS,
    }


def make_office_package(path: Path, parts: dict[str, str | bytes]) -> None:
    with zipfile.ZipFile(path, "w") as handle:
        for name, content in parts.items():
            handle.writestr(name, content)


def office_report(project: Path, *args: str) -> tuple[int, dict]:
    result = run_script("check_office.py", *args, cwd=project)
    return result.returncode, json.loads(result.stdout)


class TestCheckOffice:
    def test_clean_pptx_passes(self, tmp_path: Path) -> None:
        make_office_package(tmp_path / "deck.pptx", base_pptx_parts())
        code, report = office_report(tmp_path, "--json", "deck.pptx")
        assert code == 0, report
        entry = report["reports"][0]
        assert entry["status"] == "pass"
        assert entry["kind"] == "pptx"
        assert entry["counts"] == {"slides": 2, "hidden": 0}
        assert entry["errors"] == []
        assert entry["warnings"] == []
        assert {finding["code"] for finding in entry["info"]} == {"author-metadata"}

    def test_missing_media_fails(self, tmp_path: Path) -> None:
        parts = base_pptx_parts()
        del parts["ppt/media/image1.png"]
        make_office_package(tmp_path / "deck.pptx", parts)
        code, report = office_report(tmp_path, "--json", "deck.pptx")
        assert code == 1
        entry = report["reports"][0]
        assert entry["status"] == "fail"
        assert {finding["code"] for finding in entry["errors"]} == {"missing-media"}

    def test_placeholder_warns_and_strict_fails(self, tmp_path: Path) -> None:
        parts = base_pptx_parts()
        parts["ppt/slides/slide2.xml"] = pptx_slide("[RESULT PENDING]")
        make_office_package(tmp_path / "deck.pptx", parts)
        code, report = office_report(tmp_path, "--json", "deck.pptx")
        assert code == 0
        entry = report["reports"][0]
        assert entry["status"] == "pass-with-warnings"
        assert {finding["code"] for finding in entry["warnings"]} == {"placeholder-content"}
        strict_code, strict_report = office_report(tmp_path, "--json", "--strict", "deck.pptx")
        assert strict_code == 1
        assert strict_report["reports"][0]["status"] == "fail"

    def test_oversized_xml_part_is_not_silently_skipped(self, tmp_path: Path) -> None:
        parts = base_pptx_parts()
        parts["ppt/slides/slide2.xml"] = " " * (4 * 1024 * 1024 + 1)
        make_office_package(tmp_path / "deck.pptx", parts)
        code, report = office_report(tmp_path, "--json", "deck.pptx")
        assert code == 0
        warnings = report["reports"][0]["warnings"]
        assert {finding["code"] for finding in warnings} == {"oversized-xml-part"}
        strict_code, _ = office_report(tmp_path, "--json", "--strict", "deck.pptx")
        assert strict_code == 1

    def test_empty_and_hidden_slide_reported(self, tmp_path: Path) -> None:
        parts = base_pptx_parts()
        parts["ppt/slides/slide2.xml"] = pptx_slide("", show="0")
        make_office_package(tmp_path / "deck.pptx", parts)
        code, report = office_report(tmp_path, "--json", "deck.pptx")
        assert code == 0
        entry = report["reports"][0]
        assert entry["counts"] == {"slides": 2, "hidden": 1}
        assert {finding["code"] for finding in entry["warnings"]} == {"empty-slide"}
        assert {finding["code"] for finding in entry["info"]} == {"author-metadata", "hidden-slide"}

    def test_docx_and_xlsx_checks(self, tmp_path: Path) -> None:
        make_office_package(
            tmp_path / "report.docx",
            {
                "[Content_Types].xml": OOXML_CONTENT_TYPES,
                "word/document.xml": DOCX_DOCUMENT,
            },
        )
        code, report = office_report(tmp_path, "--json", "report.docx")
        assert code == 0, report
        docx_entry = report["reports"][0]
        assert docx_entry["kind"] == "docx"
        assert docx_entry["counts"] == {"paragraphs": 2}

        make_office_package(
            tmp_path / "data.xlsx",
            {
                "[Content_Types].xml": OOXML_CONTENT_TYPES,
                "xl/workbook.xml": XLSX_WORKBOOK,
                "xl/worksheets/sheet1.xml": XLSX_SHEET,
            },
        )
        code, report = office_report(tmp_path, "--json", "data.xlsx")
        assert code == 0
        xlsx_entry = report["reports"][0]
        assert xlsx_entry["kind"] == "xlsx"
        assert xlsx_entry["counts"] == {"sheets": 1, "worksheets": 1}
        assert xlsx_entry["status"] == "pass-with-warnings"
        assert {finding["code"] for finding in xlsx_entry["warnings"]} == {"placeholder-content"}

    def test_macro_payload_fails(self, tmp_path: Path) -> None:
        parts = base_pptx_parts()
        parts["ppt/vbaProject.bin"] = b"fake vba payload"
        make_office_package(tmp_path / "deck.pptm", parts)
        code, report = office_report(tmp_path, "--json", "deck.pptm")
        assert code == 1
        codes = {finding["code"] for finding in report["reports"][0]["errors"]}
        assert {"macro-enabled", "embedded-vba"} <= codes

    def test_unknown_and_unreadable_fail(self, tmp_path: Path) -> None:
        (tmp_path / "notes.txt").write_text("not an office file", encoding="utf-8")
        code, report = office_report(tmp_path, "--json", "notes.txt")
        assert code == 1
        assert {finding["code"] for finding in report["reports"][0]["errors"]} == {"unknown-type"}

        (tmp_path / "broken.pptx").write_text("this is not a zip archive", encoding="utf-8")
        code, report = office_report(tmp_path, "--json", "broken.pptx")
        assert code == 1
        assert {finding["code"] for finding in report["reports"][0]["errors"]} == {"unreadable-file"}


def write_markdown(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TestCheckMarkdown:
    def test_clean_document_passes(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "docs/notes.md", "# Notes\n\n## Details\n\nText.\n")
        write_markdown(tmp_path, "README.md", "# Title\n\nSee [notes](docs/notes.md#details).\n")
        result = run_script("check_markdown.py", "README.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "status: pass" in result.stdout

    def test_unclosed_fence_fails(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n```python\ncode\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 1
        assert "unclosed-fence" in result.stdout

    def test_closing_fence_with_info_string_stays_open(self, tmp_path: Path) -> None:
        # Per CommonMark a closing fence is bare; "```python" inside the block
        # is content, and the final bare fence closes it.
        write_markdown(tmp_path, "doc.md", "# A\n\n```python\ncode\n```python\nmore\n```\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_tilde_fence_not_closed_by_backtick_fence(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n~~~\n```\n~~~\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_backtick_in_fence_info_string_is_not_a_fence(self, tmp_path: Path) -> None:
        # A backtick fence whose info string contains a backtick is not a fence
        # opener, so the trailing bare fence opens a block that never closes.
        write_markdown(tmp_path, "doc.md", "# A\n\n```x `y`\ntext\n```\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 1
        assert "unclosed-fence" in result.stdout

    def test_unresolved_marker_fails(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\nResult: [RESULT PENDING]\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 1
        assert "unresolved-placeholder" in result.stdout

    def test_marker_in_fenced_block_ignored(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n```text\n[RESULT PENDING] example\n```\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_marker_in_inline_code_ignored(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\nUse `[CITATION NEEDED]` markers.\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_broken_relative_link_fails(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n[x](missing.md)\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 1
        assert "broken-link" in result.stdout

    def test_missing_anchor_warns_and_strict_fails(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n[x](#nope)\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0
        assert "missing-anchor" in result.stdout
        strict = run_script("check_markdown.py", "--strict", "doc.md", cwd=tmp_path)
        assert strict.returncode == 1

    def test_generated_and_custom_anchors_resolve(self, tmp_path: Path) -> None:
        text = "# A\n\n## Section Two\n\n[x](#section-two)\n\n<a name=\"manual\"></a>\n\n[y](#manual)\n"
        write_markdown(tmp_path, "doc.md", text)
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_reference_style_link_targets_are_checked(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\nSee [the notes][notes].\n\n[notes]: missing.md\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 1
        assert "broken-link" in result.stdout

    def test_undefined_link_reference_warns(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\nSee [the notes][nowhere].\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0
        assert "undefined-link-reference" in result.stdout
        strict = run_script("check_markdown.py", "--strict", "doc.md", cwd=tmp_path)
        assert strict.returncode == 1

    def test_reference_definition_with_valid_target_passes(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "docs/notes.md", "# Notes\n\n## Details\n\nText.\n")
        write_markdown(
            tmp_path, "doc.md", "# A\n\nSee [the notes][notes].\n\n[notes]: docs/notes.md#details\n"
        )
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "status: pass" in result.stdout

    def test_custom_anchor_on_heading_line_resolves(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", '# A\n\n## Foo <a id="bar"></a>\n\n[x](#bar)\n\n[y](#foo)\n')
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "missing-anchor" not in result.stdout

    def test_duplicate_heading_anchor(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "docs/notes.md", "# Notes\n\n## Same\n\n## Same\n")
        write_markdown(tmp_path, "README.md", "# T\n\n[a](docs/notes.md#same-1)\n")
        result = run_script("check_markdown.py", "README.md", cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_empty_alt_text_warns(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "img.png", "")
        write_markdown(tmp_path, "doc.md", "# A\n\n![](img.png)\n")
        result = run_script("check_markdown.py", "--json", "doc.md", cwd=tmp_path)
        assert result.returncode == 0
        codes = {finding["code"] for finding in json.loads(result.stdout)["reports"][0]["warnings"]}
        assert codes == {"empty-alt-text"}

    def test_heading_structure_warnings(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n### Deep\n\n# B\n")
        result = run_script("check_markdown.py", "--json", "doc.md", cwd=tmp_path)
        assert result.returncode == 0
        codes = {finding["code"] for finding in json.loads(result.stdout)["reports"][0]["warnings"]}
        assert codes == {"heading-level-skip", "multiple-h1"}

    def test_root_relative_link_warns(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n[x](/assets/file.txt)\n")
        result = run_script("check_markdown.py", "doc.md", cwd=tmp_path)
        assert result.returncode == 0
        assert "root-relative-link" in result.stdout

    def test_external_link_and_draft_marker(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "doc.md", "# A\n\n[spec](https://spec.commonmark.org/)\n\nTODO fix this.\n")
        result = run_script("check_markdown.py", "--json", "doc.md", cwd=tmp_path)
        assert result.returncode == 0
        report = json.loads(result.stdout)["reports"][0]
        assert report["status"] == "pass-with-warnings"
        assert {finding["code"] for finding in report["warnings"]} == {"draft-marker"}

    def test_json_report_structure_and_overall_status(self, tmp_path: Path) -> None:
        write_markdown(tmp_path, "a.md", "# A\n\n[x](missing.md)\n")
        write_markdown(tmp_path, "b.md", "# B\n\nAll settled.\n")
        result = run_script("check_markdown.py", "--json", "a.md", "b.md", cwd=tmp_path)
        assert result.returncode == 1
        report = json.loads(result.stdout)
        assert report["status"] == "fail"
        statuses = {entry["file"]: entry["status"] for entry in report["reports"]}
        assert statuses == {"a.md": "fail", "b.md": "pass"}

    def test_unreadable_file_fails(self, tmp_path: Path) -> None:
        result = run_script("check_markdown.py", "absent.md", cwd=tmp_path)
        assert result.returncode == 1
        assert "unreadable-file" in result.stdout


sys.path.insert(0, str(SCRIPTS))


def tiny_drawio(tmp_path: Path) -> Path:
    source = tmp_path / "fig.drawio"
    source.write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<mxfile host=\"app.diagrams.net\"><diagram name=\"p\" id=\"p\">"
        "<mxGraphModel pageWidth=\"200\" pageHeight=\"100\"><root>"
        "<mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/>"
        "<mxCell id=\"box\" value=\"A\" style=\"rounded=1;fontSize=12;\" vertex=\"1\" parent=\"1\">"
        "<mxGeometry x=\"10\" y=\"10\" width=\"60\" height=\"30\" as=\"geometry\"/></mxCell>"
        "</root></mxGraphModel></diagram></mxfile>\n",
        encoding="utf-8",
    )
    return source


class TestRenderDrawio:
    def test_embed_page_carries_escaped_xml(self, tmp_path: Path) -> None:
        import render_drawio

        source = tiny_drawio(tmp_path)
        page = render_drawio.build_embed_page(source.read_text(encoding="utf-8"))
        assert "viewer-static.min.js" in page
        assert "&quot;" in page
        assert 'class="mxgraph"' in page
        assert "<mxfile" not in page  # raw XML must be attribute-escaped

    def test_missing_source_fails(self, tmp_path: Path) -> None:
        result = run_script("render_drawio.py", "absent.drawio", cwd=tmp_path)
        assert result.returncode == 2
        assert "source not found" in result.stderr

    @pytest.mark.skipif(
        os.environ.get("RENDER_E2E") != "1",
        reason="headless render requires playwright, a browser, and network; set RENDER_E2E=1",
    )
    def test_headless_render_produces_png_and_svg(self, tmp_path: Path) -> None:
        source = tiny_drawio(tmp_path)
        result = run_script("render_drawio.py", str(source), cwd=tmp_path)
        assert result.returncode == 0, result.stderr
        assert (tmp_path / "fig.png").is_file()
        assert (tmp_path / "fig.svg").is_file()
