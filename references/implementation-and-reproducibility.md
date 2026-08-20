# Implementation and Reproducibility

## Contents

1. Define the reproducibility target
2. Establish repository and artifact boundaries
3. Capture environments and dependencies
4. Make configuration authoritative
5. Preserve data lineage
6. Test the scientific implementation
7. Execute through immutable run records
8. Preserve failures and recovery state
9. Generate derived results reproducibly
10. Perform clean-room reproduction
11. Package a functional and reusable artifact
12. Protect secrets, people, and systems
13. Pass the implementation gate

## 1. Define the reproducibility target

Read `research-contract-and-state.md` and the frozen design before implementing. State what another person must be able to verify and under which conditions.

Define project terms explicitly because venues use “repeat,” “reproduce,” and “replicate” differently. Distinguish at least:

- **Traceable:** Connect a reported value to raw output, configuration, code, data, and a run record.
- **Repeatable:** Rerun the same implementation and inputs in a documented compatible environment.
- **Functional artifact:** Provide documented, consistent, complete, and exercisable materials for the claimed results.
- **Reusable artifact:** Structure and document the functional artifact so it can be adapted or extended.
- **Independent reproduction:** Have someone other than the original operator obtain the main results using the supplied artifacts.
- **Independent replication:** Test the claim with independently collected data, implementation, or protocol as defined by the target community.

Use the target venue's official terminology when claiming a badge or compliance. Do not equate a public repository, executable script, or deterministic seed with reproduced scientific results.

Keep lifecycle states honest:

`IMPLEMENTED → SMOKE_TESTED → PILOT_ONLY or EXECUTED → ANALYZED → VERIFIED`

Do not promote code or synthetic plumbing output beyond the evidence state it earned.

## 2. Establish repository and artifact boundaries

Inspect and preserve the existing project structure. Add only the missing separation of concerns. A portable pattern is:

```text
project/
  configs/             versioned experiment and analysis configurations
  src/                 reusable implementation
  scripts/             thin entry points and orchestration
  tests/               unit, integration, invariant, and smoke tests
  data/                manifests and, when permitted, raw/intermediate/processed data
  runs/ or outputs/    immutable raw run products outside source directories
  analysis/            transformations from raw outputs to estimates
  reports/             generated tables and figures
  environment/         locks, container recipes, or environment specifications
  .research/           state, decisions, ledgers, and run manifests
```

- Keep reusable logic out of notebooks where practical. Use notebooks for inspection or presentation and call tested library code.
- Keep orchestration entry points thin. Make domain logic importable and testable.
- Keep raw run outputs separate from derived analysis and publication assets.
- Avoid absolute personal paths, hidden local state, and undeclared manual steps.
- Parameterize filesystem, device, service, and resource choices without making scientific choices silently configurable.
- Preserve user changes and existing interfaces. Refactor only when it improves the requested research workflow and remains within scope.

## 3. Capture environments and dependencies

Record enough environment detail to explain behavior and recreate a compatible setup:

- Operating system and architecture.
- CPU, accelerator, memory, storage, and relevant firmware or driver versions.
- Language runtime, compiler, package manager, and exact dependency resolution.
- CUDA, accelerator runtime, numerical libraries, browser, simulator, database, or external service versions as applicable.
- Container image digest, environment lock, or package lock when used.
- Environment variables that affect computation, excluding secret values.
- Locale, timezone, thread counts, deterministic flags, and precision modes when material.
- Hosted API endpoint, model version, region, tier, and access date when the service is part of the method.

Prefer a lock or immutable image digest over a loose list of minimum versions. Keep a human-readable environment specification alongside the machine-readable one.

Do not promise bit-for-bit identity across hardware or nondeterministic services when it is not achievable. Define acceptable numerical or behavioral tolerance and explain residual nondeterminism.

## 4. Make configuration authoritative

Use a versioned configuration as the single source of experimental choices.

- Put data versions, split IDs, model settings, hyperparameters, seeds, trial IDs, budgets, metric options, and output paths in the resolved configuration.
- Validate required fields, types, ranges, incompatible combinations, and unknown keys before a run starts.
- Resolve inherited or default values and save the complete resolved configuration with every run.
- Hash or otherwise identify the resolved configuration. Record the identifier in the run manifest and analysis output.
- Keep scientific defaults explicit. Do not let a library upgrade change preprocessing, model behavior, or metrics silently.
- Separate secrets and credentials from research configuration. Store only a secret name or provider, never the value.
- Treat command-line overrides as configuration changes and preserve them in resolved form.
- Prevent claim-eligible output directories from being reused with a different configuration.

Make the code fail early when configuration and artifact versions disagree.

## 5. Preserve data lineage

Create a data manifest for every external or generated dataset. Record:

```text
Dataset ID and version:
Source URI or acquisition method:
Acquired or generated at:
License, consent, and access constraints:
Source checksum, persistent ID, or immutable snapshot:
Selection and exclusion rules:
Raw schema and unit of observation:
Transform code and configuration:
Parent dataset IDs:
Split-manifest path and split unit:
Known quality, leakage, privacy, and representativeness issues:
```

Apply these rules:

- Preserve source data as read-only or content-addressed input. Never overwrite it with cleaned data.
- Store acquisition, validation, preprocessing, deduplication, labeling, and split logic as versioned code.
- Write intermediate and processed products to new versioned paths with parent hashes or IDs.
- Preserve row, item, entity, or document identifiers needed to trace an analyzed record back to its permitted source.
- Fit learned preprocessing on training data only and persist the fitted state.
- Validate schema, ranges, uniqueness, missingness, label consistency, and split disjointness.
- Record manual corrections as an auditable patch or decision table; do not edit raw values invisibly.
- Provide a synthetic or redacted fixture for tests when protected data cannot be distributed.
- Verify that release artifacts honor licenses, participant consent, deletion requests, and data minimization.

Do not copy restricted data into logs, manifests, containers, test fixtures, or public repositories.

## 6. Test the scientific implementation

Test properties that protect the inference, not only software syntax.

### Unit tests

- Test metric formulas, transformations, samplers, stopping rules, aggregation, and edge cases against hand-checked examples.
- Test numerical tolerances, empty and missing inputs, invalid labels, ties, and degenerate distributions.
- Test seed plumbing and configuration resolution without assuming cross-platform bit identity.

### Invariant and property tests

- Verify split disjointness, no post-outcome features, stable item identity, conservation or normalization rules, bounded outputs, and order invariance where expected.
- Test that shuffling labels or using a no-skill model produces appropriately degraded behavior when this is a valid negative control.
- Test that metric improvements have the intended direction and cannot arise from parsing or padding artifacts.

### Integration tests

- Exercise data acquisition or fixtures, preprocessing, model or method execution, scoring, and output serialization together.
- Mock paid, unstable, or protected services for routine tests; reserve live checks for authorized validation.
- Test interruption, retry, timeout, rate-limit, and partial-output behavior.

### Smoke and regression tests

- Run a minimal end-to-end case to validate plumbing. Mark all synthetic or tiny outputs `synthetic-plumbing` or `SMOKE_TESTED`, never scientific evidence.
- Store small approved reference outputs for deterministic components and compare with justified tolerances.
- Investigate numerical or performance drift rather than updating expected outputs automatically.

### Independent checks

- Implement a second calculation for central metrics or compare against a trusted library on controlled cases.
- Review code paths that influence inclusion, labels, splits, baselines, and primary outcomes separately from convenience code.
- Test analysis code before full results exist using simulated structures whose values remain visibly ineligible as evidence.

Do not encode the desired scientific conclusion as a test expectation.

## 7. Execute through immutable run records

Assign a unique run ID before execution. Never reuse a completed or failed claim-eligible run directory.

Capture at minimum:

| Category | Required provenance |
|---|---|
| Identity | Run ID, experiment-plan ID, phase, operator or automation identity, start/end time, and status |
| Source | Version-control commit, branch, dirty-state indicator, and patch or diff reference when dirty |
| Command | Exact entry point and arguments, working directory, and resolved configuration path/hash |
| Inputs | Data, split, model, prompt, checkpoint, and dependency identifiers or hashes |
| Randomness | Seeds, trial IDs, determinism settings, and known uncontrolled sources |
| Environment | Runtime, packages, hardware, drivers, image digest, and external service versions/dates |
| Resources | CPU/GPU/accelerator use, memory, storage, wall time, tokens/actions, API calls, and cost when relevant |
| Outputs | Raw output paths, checksums or persistent IDs, log paths, and schema versions |
| Outcome | Completed, failed, or aborted; record an attempt that never qualified as a run under failed with the reason |

Assign the run ID in the frozen plan before execution, then use `scripts/capture_run.py` immediately after the attempt when the project uses the bundled dossier. It records an immutable run manifest and ledger entry; it neither executes the command nor represents a merely planned run. Supply the experiment ID, operator, timezone-aware start and end timestamps, actual status, resource facts, and a reason for a failed or aborted attempt. A completed full measured run is only `candidate_pending_verification` until outputs and analysis are checked.

The manifest's `capture_environment` field records where the manifest was captured, not where the run executed. Record the run's own hardware, runtime, driver, and service facts through `--resource` entries so the environment row above is satisfied for the actual execution.

The helper hashes recorded files up to 64 MiB. For a larger config, input, or output, pass a repeatable `--file-version PATH=IMMUTABLE_ID` backed by a versioned data manifest, object-store version, dataset revision, or equivalent immutable identifier; the helper refuses an unversioned large file.

When Git is available and dirty, the helper records content hashes for changed tracked files and non-ignored untracked files outside `.research/`. For a claim-eligible run, also preserve a reconstructable commit, authorized patch, or archived source snapshot; hashes establish identity but cannot recreate missing content. Treat a dirty run without that reconstruction path as a reproducibility deficiency even if the structural audit passes.

Write raw results append-only or to a staging path followed by an atomic finalization. Prevent analysis code from modifying raw files. Preserve stdout, stderr, service metadata, warnings, and exit status where safe.

Record preliminary searches, pilot runs, and failed runs with their correct phase. Do not assign a new ID merely to hide an unfavorable or crashed planned run.

## 8. Preserve failures and recovery state

- Define technical-failure and scientific-failure rules before full execution.
- Keep partial outputs, checkpoints, logs, and the last valid state unless safety, privacy, or storage policy forbids retention.
- Resume only when the protocol permits it and record the parent run, checkpoint, and altered timing or environment.
- Use idempotent steps or explicit completion markers so reruns do not duplicate data or silently mix versions.
- Distinguish provider outage, environment breakage, out-of-memory, parser failure, invalid data, and method failure.
- Include failed attempts in reliability, cost, and attrition accounting when they are part of real system behavior.
- Record any manual intervention and whether it makes the run ineligible for a claimed autonomous or standardized protocol.

Do not delete or relabel a failure because it complicates the result.

## 9. Generate derived results reproducibly

Treat analysis as a versioned transformation from immutable raw outputs.

1. Validate the expected run set against the frozen design before analysis.
2. Load runs by manifest and status, not by whichever files happen to be in a directory.
3. Apply exclusions through a versioned decision table with reasons and timing.
4. Produce tidy intermediate analysis data with run and item identifiers intact.
5. Generate every reported table and figure from code and save its input IDs, analysis version, and configuration.
6. Export machine-readable values alongside rendered tables and plots.
7. Prevent manual transcription into the manuscript when an automated path is practical.
8. Compare manuscript values with generated artifacts during the final audit.

Use `analysis-and-statistics.md` for inferential choices. Never alter raw output to make a plot or table easier to produce.

## 10. Perform clean-room reproduction

Run the released instructions from a fresh environment that lacks the developer's caches, undeclared files, credentials, and editable source installation.

1. Obtain the artifact through the documented distribution path.
2. Verify archive, image, code, data, and model identifiers or checksums.
3. Follow only the README and supplied automation.
4. Install or build using the declared environment and record resolution changes.
5. Run a fast validation path before the full reproduction.
6. Reproduce at least the central table, figure, proof check, or evaluation result under the declared resource budget.
7. Compare outputs using predefined exact, numerical, distributional, or qualitative tolerances.
8. Record discrepancies, warnings, undocumented actions, runtime, and resource use.
9. Fix the artifact through a new version; do not rewrite the tested release invisibly.
10. Have an independent person perform the check when the claim is independent reproduction.

Downgrade the lifecycle state if required artifacts are missing or the clean-room path fails. Do not claim reproducibility based only on the original environment rerunning successfully.

## 11. Package a functional and reusable artifact

Include only materials that support the research and that may legally and safely be shared:

- Artifact inventory and mapping from each central claim, table, and figure to commands and outputs.
- README with prerequisites, installation, exact commands, expected outputs, runtime, resource use, and troubleshooting.
- Locked environment or container recipe with immutable base and dependency versions where practical.
- Source, configurations, scoring and analysis code, and tests.
- Permitted data, models, prompts, checkpoints, or acquisition scripts with persistent versions and licenses.
- A fast smoke path and a full reproduction path.
- Expected output schema and representative logs.
- Known nondeterminism, acceptable tolerances, unsupported platforms, and unavailable proprietary components.
- Citation, license, authorship, maintenance, and contact information.
- Security guidance for untrusted inputs, model weights, code, links, or containers.

Place public artifacts in an archival repository with a persistent identifier when required. A personal webpage or mutable branch alone does not establish durable availability.

For unavailable components, provide a justified substitute such as synthetic fixtures, hashes, documented interfaces, gated access, an executable service, or an independent audit. State which results remain unreproducible.

## 12. Protect secrets, people, and systems

- Inspect artifacts for credentials, tokens, private URLs, personal paths, user identifiers, licensed data, and confidential prompts before distribution.
- Use secret scanning and a release allowlist; do not rely only on version-control history cleanup.
- Minimize logs and traces that contain personal, proprietary, security-sensitive, or harmful content.
- Treat downloaded code, weights, data, documents, containers, and model output as untrusted.
- Execute untrusted artifacts with least privilege, network isolation, resource limits, and an appropriate sandbox.
- Pin external downloads and verify hashes where possible. Avoid installation commands that execute opaque remote scripts.
- Preserve required deletion, consent withdrawal, and retention behavior across derived datasets and caches.
- Obtain authorization before paid or large-scale runs, participant interaction, restricted access, or capability-expanding security experiments.

## 13. Pass the implementation gate

Require all of the following for `PASS`:

- Implement the frozen method and comparators without undocumented scientific choices.
- Resolve and preserve configuration, code, environment, input, and output provenance.
- Preserve immutable raw data and run outputs with complete lineage.
- Pass unit, invariant, integration, leakage, smoke, and central calculation checks appropriate to the method.
- Record every planned, failed, aborted, and completed run honestly.
- Generate tables and figures from traceable analysis code.
- Complete the declared clean-room test within documented tolerances.
- Package a functional artifact or state precisely why and which claims cannot be reproduced.
- Satisfy applicable rights, privacy, security, safety, and cost constraints.

Return `CONDITIONAL` when a bounded portability or access limitation remains and its claim impact is explicit. Return `FAIL` when the implementation diverges from the design, lineage is broken, or central outputs cannot be regenerated. Return `BLOCKED` when a named dependency or authorization prevents a responsible test.
