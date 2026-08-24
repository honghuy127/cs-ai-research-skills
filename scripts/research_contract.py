"""Shared, dependency-free contracts for the bundled research tools.

Keep controlled values here so dossier validation, run capture, audits, and
artifact checkers cannot silently diverge. This module is internal; users call
the executable scripts that import it.
"""

from __future__ import annotations

DOSSIER_SCHEMA_VERSION = "1.0"
MANIFEST_SCHEMA_VERSION = "1.1"
SUPPORTED_MANIFEST_SCHEMAS = frozenset({"1.0", MANIFEST_SCHEMA_VERSION})

MAX_HASH_BYTES = 64 * 1024 * 1024
PLACEHOLDERS = ("[CITATION NEEDED]", "[EVIDENCE NEEDED]", "[RESULT PENDING]")

VALID_STAGES = frozenset(
    {
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
)
VALID_STATUSES = frozenset(
    {
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
)
VALID_EVIDENTIAL_STATUSES = frozenset(
    {"not_assessed", "insufficient", "supported", "mixed", "contradicted"}
)
VALID_CLAIM_TYPES = frozenset(
    {
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
)
VALID_EVIDENCE_VERIFICATIONS = frozenset(
    {"metadata-only", "abstract-checked", "full-text-checked", "artifact-checked"}
)
VALID_PUBLICATION_STATUSES = frozenset(
    {"published", "accepted", "preprint", "unpublished", "unknown"}
)
VALID_PEER_REVIEW_STATUSES = frozenset(
    {"peer-reviewed", "not-peer-reviewed", "unknown"}
)
VALID_RUN_PHASES = frozenset({"smoke", "pilot", "full"})
VALID_RUN_STATUSES = frozenset({"completed", "failed", "aborted"})
VALID_RESULT_KINDS = frozenset({"none", "measured", "synthetic-plumbing"})
VALID_EVIDENCE_ELIGIBILITY = frozenset(
    {"candidate_pending_verification", "not_scientific_evidence"}
)

EVIDENCE_BEARING_STATUSES = frozenset({"supported", "mixed", "contradicted"})
EXECUTION_BEARING_STATES = frozenset({"executed", "analyzed", "verified", "reported"})
INDEPENDENT_CHECK_STATES = frozenset({"verified", "reported"})
EMPIRICAL_TYPES = frozenset(
    {"empirical", "causal", "performance", "efficiency", "human-evaluation"}
)

LEDGERS = ("evidence.jsonl", "claims.jsonl", "experiments.jsonl")
