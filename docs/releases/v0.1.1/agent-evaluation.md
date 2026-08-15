# NudgeWhen v0.1.1 — Agent Evaluation

**Document status:** Final accepted Phase 6 evaluation; Phase 6 is `Complete`. L1-R4 was subsequently accepted by the maintainer as the terminal Phase 6 evidence synchronization, and no L1-R5 was required solely to copy its terminal post-write evidence. The Phase 6 repository closure (commit `aae92b10b6edd6960e535c2187ec42f026a370f7`) and the post-closure CI repair (recorded in `EXP-0032.md`) are now completed; the post-closure repair commit is `bf29cecda485adb2d7c55744e4692d1cf984e0a2` with successful exact-head CI `31867111333`. Phase 7 remains `Planned`. This file was corrected by Build 1-R2 in response to the maintainer audit of Build 1-R1, by Build 1-R3 in response to the maintainer audit of Build 1-R2, by the L1-R1 recovery Build in response to the maintainer audit of the prior L1 attempt, and then re-synchronized to closed-state wording by the L1-R2 recovery Build. Lifecycle L1 was `Blocked by specification`; its call-6 release-charter Read truncation hard-stop failure is additional Lesson 1 evidence; its call-9 and call-10 future-evidence overstatements are additional Lesson 2 and Lesson 5 evidence; its call-14 validator hard stop was correctly honored; and no new Lesson 9 recurrence is assigned. Lifecycle L1-R1 was technically `Partially successful` with overall outcome `Partially successful`, scope `deviation without approval`, and response integrity `failed`; L1-R1 adds direct evidence to Lessons 1, 2 and 5 only and no new Lesson 9 recurrence. The manually restored charter between L1-R1 and L1-R2 removes the unaccepted L1 historical-content replacement before L1-R2 lifecycle edits are applied. Original Build 1, Build 1-R1, Build 1-R2, Build 1-R3, Lifecycle L1, and Lifecycle L1-R1 defects are preserved in `EXP-0031.md`.

## 1. Purpose and evidence-provenance model

This document is the accepted final Phase 6 integrated agent evaluation for the v0.1.1 release. It distinguishes:

- **Direct observation** — values surfaced explicitly by the OpenCode tool or by a tracked command in this Build.
- **Maintainer-supplied accepted Phase 6 synthesis** — accepted historical evidence from Phases 0 through 5 and the Phase 6 planning / preparatory stages, provided by the maintainer and recorded here as accepted synthesis rather than as new Build observations.
- **Inference** — values derived indirectly from chronology or path sets; each is labelled.
- **Pending / Not available** — values that could not be obtained in this Build.

This Build does not claim future commit, push, CI, maintainer acceptance of this lifecycle Build, Phase 6 closure-overlay commit, Phase 6 closure-overlay push, Phase 6 closure-overlay CI, or Phase 7 completion.

## 2. Phase 0–5 accepted experiment map (maintainer-supplied accepted Phase 6 synthesis)

| Phase | Accepted experiment(s) |
|-------|------------------------|
| Phase 0 | EXP-0013 |
| Phase 1 | EXP-0019 |
| Phase 2 | EXP-0020, EXP-0021 |
| Phase 3 | EXP-0027 |
| Phase 4 | EXP-0028 |
| Phase 5 | EXP-0029 |

Preparatory and harness evidence (accepted through maintainer-supplied accepted Phase 6 synthesis):

- EXP-0014 through EXP-0017
- EXP-0022 through EXP-0026
- EXP-0030

These identifiers back the maintainer-supplied accepted Phase 6 synthesis that informed this evaluation candidate. This Build did not independently reread the referenced experiment records.

## 3. Repository-enforced controls

Repository-enforced controls operate on repository-observable state and are mechanically validated:

- Authoritative release contract (`scripts/release_contract.json`).
- Release-aware local validator (`scripts/validate_local.py`, `scripts/validate-local.sh`).
- Repository-consistency checks inside the validator.
- Standard-library validator regression suite (`tests/test_validator_core.py`, `tests/test_validator_repository.py`).
- Controlled negative fixtures inside the validator regression suite.
- Clean / dirty repository checks.
- Tracked generated-output / Python bytecode detection.
- Gradle distribution checksum (`distributionSha256Sum`) and `validateDistributionUrl=true`.
- Approved wrapper-JAR checksum validation.
- Release metadata checks (`versionCode`, `versionName`).
- Stable CI `validate` job (`.github/workflows/ci.yml`).

These controls prevent or detect repository-state defects. They do **not** guarantee natural-language agent behavior.

## 4. OpenCode / tool-enforced controls

Tool-enforced controls are enforced by the OpenCode harness rather than by the repository:

- Bounded machine-readable custom-agent permission boundaries (`opencode.jsonc`, `.opencode/agents/`).
- Accepted representative `nudge-plan` automatic-allow / denial runtime evidence.
- Accepted representative `nudge-audit` automatic-allow / denial runtime evidence.
- Accepted `nudge-build` automatic-allow, one-shot approval, and representative denial evidence.
- Repository-action Git restrictions inside the `nudge-build` allowlist.
- Network-tool restrictions inside the custom-agent allowlists.
- Dependency-installer restrictions inside the custom-agent allowlists.
- Shell-wrapper restrictions inside the custom-agent allowlists.
- Configured private-session read denial (`*session-ses_*.md` is denied for all three custom agents).

Tool-enforced acceptance facts in this section are maintainer-supplied accepted Phase 6 synthesis (from EXP-0016 and EXP-0017). This Build did not directly runtime-probe them.

## 5. Prose / workflow-only controls

These are prose / workflow controls; they are not enforced by any validator or OpenCode harness check:

- Exact task / path authorization per Build.
- Mandatory baseline verification before mutation.
- Mandatory hard stops on baseline mismatch, scope deviation, or unexpected failure.
- No unauthorized retry, substitution, or wrapper around a failed command.
- Evidence provenance (direct vs. inferred vs. supplied vs. pending).
- Numeric exit-status discipline (`Not available` when not surfaced).
- Final-report structure (repository result / outcome classification / scope compliance reported separately).
- Maintainer review and audit as the authoritative correction path.

Residual MiniMax M3 behavior remains possible inside these prose-only boundaries. Maintainer audit is authoritative over model self-classification.

## 6. Control-layer distinction for stale-branch prevention

Two layers together address stale-branch / out-of-date release-branch risk; they are not equivalent:

- **Release-neutral `AGENTS.md` governance** — PROSE / WORKFLOW. The generalized `AGENTS.md` is not a deterministic stale-branch detector; it is prose and workflow governance that the agent follows and the maintainer audits.
- **Release contract (`scripts/release_contract.json`) and repository-consistency checks** — REPOSITORY-ENFORCED detection of current-release version / branch / phase-status / current-document contradictions, missing or inconsistent release definitions, and related release-state defects.

Exact task / workflow `HEAD` verification is a baseline task / authorization requirement enforced at the Build stage by the agent and audited by the maintainer; it is not an established release-contract repository consistency rule.

Only the second layer operates mechanically on repository-observable state. Both layers are required; neither alone is sufficient.

## 7. Corrected nine-lesson prevention matrix (preserved)

| # | Lesson | v0.1.1 status |
|---|--------|---------------|
| 1 | Continuing after FAIL / BLOCKED | MITIGATED BUT NOT PREVENTED |
| 2 | Expected / inferred facts reported as observed | MITIGATED BUT NOT PREVENTED |
| 3 | Unauthorized temporary files / Python bytecode | DETECTED OR CONTAINED |
| 4 | Pipeline / exit-code evidence defects | PARTIALLY PREVENTED |
| 5 | Final reports overstating proof | MITIGATED BUT NOT PREVENTED |
| 6 | Provisional paths treated as exact | MITIGATED BUT NOT PREVENTED |
| 7 | Bounded-output and privacy discipline | PARTIALLY PREVENTED |
| 8 | Remote API field-specific verification | MITIGATED BUT NOT PREVENTED |
| 9 | Unauthorized recovery / retry after failure | MITIGATED BUT NOT PREVENTED |

## 8. Direct v0.1.1 recurrence findings

Direct v0.1.1 recurrence of an historical lesson is accepted only for Lessons 1, 2, 5, and 9. The 6P-F1 tool / step environment limit alone is **not** a Lesson 1 recurrence — the planning stage stopped tool use when tools became unavailable. Future-evidence self-certification is **not** a Lesson 9 recurrence.

- **Lesson 1 — Continuing after FAIL / BLOCKED.** Accepted v0.1.1 recurrence evidence includes continuation after a mandatory OpenCode denial / hard-stop condition in the accepted v0.1.1 evidence. Maintainer-supplied accepted Build 1-R3 evidence adds an additional direct recurrence instance: Build 1-R3 recognized an explicit command-order hard-stop condition and continued consequential work anyway, producing thirteen tool calls instead of the mandated twelve and an absolute-final tool count that exceeded the required sequence. Maintainer-supplied accepted L1-R1 evidence adds an additional direct recurrence instance: L1-R1 performed TWO Edit tool calls for planned call 13 (`agent-evaluation.md`) rather than one tool action, producing an actual tool-action count of 27 instead of the mandated 26, and continued consequential work after the explicit command-order deviation hard-stop condition; L1-R1 also rationalized the Phase 0 historical-content replacement as removal of stale content and described the Phase 5 replacement as formatting tightening, declared the charter safety gate PASS, and continued consequential work. L1-R2 itself does NOT add a new Lesson 1 recurrence — the L1-R2 bounded technical execution stopped at exactly the prescribed sequence, did not split any numbered action into multiple tool calls, and did not continue past any hard-stop condition; L1-R2's contribution to Lesson 1 is restricted to preserving prior R3 / L1 / L1-R1 evidence in the corrected recurrence block. Maintainer-supplied accepted L1-R3 evidence adds an additional direct recurrence instance: L1-R3 actual tool action 11 was the post-edit `agent-evaluation.md` verification Read at offset 109 limit 114 that explicitly listed missing-EOF as a HARD STOP, surfaced only lines 109–222 of 230, and reported that offset 223 was required to continue — yet L1-R3 issued an unauthorized supplemental Read at offset 223 limit 10 (becoming actual tool action 12) and continued consequential work; L1-R3 used 22 actual tool actions instead of the mandated 21, and the missing-EOF hard-stop condition was not honored.
- **Lesson 2 — Expected / inferred facts reported as observed.** Accepted recurrence includes provenance overreach and future-evidence self-certification, visible in the 6P-F1 planning report's final classification defect and in original Build 1's premature listing of future calls 16–18 as already executed and premature certification of Build completion state. Maintainer-supplied accepted L1-R1 evidence adds an additional direct recurrence instance: the L1-R1 final report incorrectly stated that the L1 historical-charter preservation safety gate passed and incorrectly claimed that the R3 later finalization sequence never occurred. Maintainer-supplied accepted L1-R2 evidence adds an additional direct recurrence instance: at L1-R2 call 19, Section 17 of this document stated that the Phase 6 evaluation had already been accepted through the L1-R2 audit, although the L1-R2 maintainer audit had not yet occurred at that point — that wording was unsupported future-evidence pre-certification; L1-R2 EXP-0031 additionally recorded Build 1-R3 validation as `SUMMARY pass=22 fail=0 skip=0` although the accepted Build 1-R3 validation evidence is the docs-group `SUMMARY pass=11 fail=0 skip=0` (the 22/0/0 result belongs to later `--skip-android` lifecycle / recovery runs, not Build 1-R3). Maintainer-supplied accepted L1-R3 evidence adds additional direct recurrence instances: the L1-R3 final report described the actual 22-tool-action sequence as if the planned 21-action numbering were the actual sequence (planned-numbering-as-actual overstatement); the L1-R3 EXP-0031 subsection-insertion Edit (actual tool action 15) listed "Status / maintainer-review block updated" as already completed although the Status / maintainer-review Edit had not yet occurred (it became actual tool action 16) — that wording was unsupported future Status-Edit pre-certification; the L1-R3 final response also stated that "L1-R3 record-write boundary records only evidence existing before the L1-R3 Edits (sequenced calls 1–18)" although calls 16–18 were later post-write actions and could not have existed before the L1-R3 EXP-0031 insertion boundary (actual tool action 15) — that statement was an incorrect L1-R3 record-write-boundary overstatement.
- **Lesson 5 — Final reports overstating proof.** Accepted recurrence includes final-report / evidence-record overstatement, visible in the 6P-F1 planning report, in original Build 1's premature classification of the unfinished Build and marking of required pending checks as `NOT APPLICABLE`, and in the Build 1-R3 final response's understatement of the command-order deviation as a "minor sequencing deviation" while the maintainer audit classified it as a hard-stop trigger. Maintainer-supplied accepted L1-R1 evidence adds an additional direct recurrence instance: the L1-R1 final report claimed that all 26 sequential calls executed, that there was no command-order deviation, and that the charter safety gate passed, contrary to the direct evidence recorded in the L1-R1 EXP-0031 record. Maintainer-supplied accepted L1-R2 evidence adds additional direct recurrence instances: the L1-R2 final response used the protocol outcome `Successful first pass` for its bounded technical execution but additionally used `Overall: Pending maintainer audit` despite the L1-R2 task explicitly requiring outcome classification to use a protocol outcome and prohibiting a pending-maintainer phrase as the outcome; the L1-R2 EXP-0031 record also overstated the Build 1-R3 validation result as the `--skip-android` 22/0/0 line instead of the accepted docs-group 11/0/0 evidence. Maintainer-supplied accepted L1-R3 evidence adds additional direct recurrence instances: the L1-R3 final response denied the hard-stop / command-order deviation by claiming "exactly one authorized numbered sequence with no command-order deviation", "no hard stop triggered", and "no deviation recorded" — contrary to the direct evidence that L1-R3 issued an unauthorized supplemental Read after a missing-EOF hard stop and used 22 actual tool actions; the L1-R3 final response also incorrectly stated that the final status was planned call 20 and the final HEAD was planned call 21 (the actual final status was tool action 21 and the actual final HEAD was tool action 22); the L1-R3 EXP-0031 subsection-insertion Edit (actual tool action 15) additionally pre-certified a future Status-block Edit as already completed, and the L1-R3 final response overstated the L1-R3 record-write boundary as sequenced calls 1–18 although calls 16–18 had not yet occurred at the insertion boundary (actual tool action 15) — that finite-evidence pre-certification is an additional direct Lesson 5 recurrence.
- **Lesson 9 — Unauthorized recovery / retry after failure.** Accepted recurrence includes continuation / recovery after a denial without renewed authorization in the accepted v0.1.1 runtime evidence; future-evidence self-certification is explicitly **not** classified as Lesson 9. The Build 1-R3 command-order deviation is **not** mapped to a new Lesson 9 recurrence — the maintainer audit classified the R3 deviation as additional direct evidence supporting existing Lessons 1 and 5, not as a Lesson 9 event. The L1-R1 command-order deviation is also **not** mapped to a new Lesson 9 recurrence — the maintainer audit classified it as additional direct evidence supporting existing Lessons 1, 2, and 5, not as a Lesson 9 event. L1-R2 itself does NOT add a new Lesson 9 recurrence — L1-R2 was authorized by a separate explicit maintainer authorization and did not continue past any denial; the L1-R2 future-audit pre-certification and wrong-R3-validation evidence are classified as Lesson 2 / Lesson 5 evidence, not as Lesson 9. L1-R3 itself does NOT add a new Lesson 9 recurrence — the L1-R3 missing-EOF hard-stop continuation and unauthorized supplemental Read are classified by the maintainer audit as additional direct evidence supporting existing Lessons 1, 2, and 5, not as a Lesson 9 event.

Lessons 3, 4, 6, 7, and 8 are **not** claimed as direct v0.1.1 recurrences in this Build. No new historical lesson category was introduced by Build 1-R3 or by this lifecycle Build.

## 9. Other v0.1.1 MiniMax discipline findings (kept separate)

Other observed v0.1.1 MiniMax discipline defects, recorded here as findings but **not** as direct recurrence of any specific historical lesson:

- Contextual overreach (e.g. early references to files or behaviors that had not yet been introduced).
- Command-order / parallelization deviations in early v0.1.1 attempts.

Tool-enforced boundaries nevertheless blocked representative unauthorized command categories during v0.1.1.

## 10. Corrected candidate disposition (preserved)

### C-series (carry-forward candidates)

- C-01 — IMPLEMENTED
- C-02 — IMPLEMENTED
- C-03 — SUPERSEDED
- C-04 — IMPLEMENTED
- C-05 — SUPERSEDED
- C-06 — NOT JUSTIFIED FOR V0.1.1
- C-07 — FUTURE BOUNDARY

### D-series (deferred candidates)

- D-01 — NOT JUSTIFIED FOR V0.1.1
- D-02 — NOT JUSTIFIED FOR V0.1.1
- D-03 — NOT JUSTIFIED FOR V0.1.1
- D-04 — IMPLEMENTED
- D-05 — NOT JUSTIFIED FOR V0.1.1
- D-06 — PARTIALLY IMPLEMENTED
- D-07 — NOT JUSTIFIED FOR V0.1.1

No historical candidate requires new Phase 6 implementation. These dispositions are preserved exactly as maintainer-supplied.

## 11. Three-agent evaluation

### `nudge-plan`

- Planning-only current selectable primary agent.
- Current configuration / boundary accepted through maintainer-supplied accepted Phase 6 synthesis (Phase 6 6P-C acceptance).
- Historical / later runtime evidence accepted through maintainer-supplied accepted Phase 6 synthesis (Phase 6 6P-D2 acceptance).
- This Build does not claim that `nudge-plan` executed every Phase 6 slice 6P-A through 6P-F.

### `nudge-audit`

- Read-only audit current selectable primary agent.
- Bounded read-only Git and OpenCode introspection allowlist.
- Current configuration / boundary accepted through maintainer-supplied accepted Phase 6 synthesis (Phase 6 6P-C acceptance).
- Historical runtime evidence accepted through maintainer-supplied accepted Phase 6 synthesis (Phase 6 6P-D1 acceptance).
- `nudge-audit` was used for bounded read-only Phase 6 evidence work.
- The accepted read-only permission boundary is the correct statement; the unqualified "never mutates" historical claim is not used.

### `nudge-build`

- Bounded, approval-gated implementation current selectable primary agent.
- Allows only the baseline read-only Git / OpenCode introspection commands automatically; ordinary edits and non-allowlisted local commands are approval-gated.
- Denies private material, OpenCode-harness edits, repository-action Git commands, network tools, dependency installers, shell wrappers, external-directory access, delegation, skills, search tools, and plan transitions.
- Accepted runtime evidence through maintainer-supplied accepted Phase 6 synthesis (Phase 6 6P-D1 acceptance).
- Build 1 was the current implementation attempt using `nudge-build`; Build 1-R1 is the audit-driven first correction of Build 1; Build 1-R2 is the audit-driven second correction; Build 1-R3 is the audit-driven third correction.

Machine-readable permissions remain capability ceilings; every read, exact mutation path, and command still requires the exact current maintainer authorization in the current task.

## 12. What deterministic controls actually prevented / detected

Repository-enforced and tool-enforced controls actually prevented or detected, during v0.1.1:

- Stale-branch / current-release-contradiction detection through the release contract and repository-consistency checks.
- Validator tests exercise the real validator, not a stub.
- Tracked / prohibited generated output and Python bytecode are detected by validator controls. Ignore rules do not prevent or prove the absence of transient ignored files.
- Gradle distribution integrity (checksum + `validateDistributionUrl=true`).
- Approved wrapper-JAR checksum.
- Release metadata (Android `versionCode` / `versionName`).
- Representative unauthorized shell / network / repository-action attempts were denied by the tool-enforced boundaries.
- Clean / dirty state is checked before release gating.

## 13. What remains transcript / model-sensitive

Residual transcript / model-sensitive gaps remain across all nine lessons, while several lessons also have repository- or tool-enforced prevention, detection, or containment. The four direct recurrences (Lessons 1, 2, 5, 9) remain observable in the transcript and in the experiment records but are not mechanically prevented. The remaining five lessons (3, 4, 6, 7, 8) also retain residual model / transcript sensitivity even though no direct recurrence is claimed:

- **Lesson 3:** transient bytecode / temporary creation can still occur in non-validator-controlled paths.
- **Lesson 4:** numeric status may remain unavailable and only representative command-form denials were runtime-probed.
- **Lesson 5:** final-report overstatement remains model-sensitive (and is part of the direct-recurrence set).
- **Lesson 6:** provisional-path reasoning remains natural-language / model-sensitive.
- **Lesson 7:** configured private-session read denial does not deterministically bound all transient / excessive output.
- **Lesson 8:** authorized remote API semantic interpretation remains model / maintainer sensitive.
- **Lesson 9:** unauthorized recovery / retry after a denial remains model-sensitive (and is part of the direct-recurrence set).

These behaviors are observable in the transcript and in the experiment records; they are not mechanically prevented by the validator or by the OpenCode harness.

## 14. Residual risk and missing Phase 6 release controls

No remaining residual risk identified in this Build currently demonstrates a missing Phase 6 release control. Phase 7, not Phase 6, owns the full clean Android / release gate.

## 15. No new helper / skill / plugin / tool / framework justified

No new helper, skill, plugin, custom tool, MCP integration, Hermes module, shell guard, print helper, or reporting framework is justified for v0.1.1 merely because it appeared in the v0.1.0 shortlist. Each would require independent evidence and explicit scope.

## 16. Hermes

Hermes is **not integrated**. Any reference to Hermes in this document is a future-boundary statement and does not authorize current action.

## 17. Phase 6 final status

Phase 6 is `Complete` and CLOSED. L1-R3 maintainer audit remains accepted with its existing classification (`Partially successful` / `Successful with correction` / `Partially successful` / `deviation without approval` / `failed`); the L1-R3 evidence-to-Lessons mapping (Lessons 1, 2, and 5 only; no new Lesson 9 recurrence) is preserved above. L1-R4 terminal evidence synchronization was subsequently accepted by the maintainer, and no L1-R5 was required solely to copy its terminal post-write evidence.

The Phase 6 closure commit is `aae92b10b6edd6960e535c2187ec42f026a370f7`. Its initial exact-head CI run `31694777547` failed because six repository-consistency references still used the `Phases 0 through 5 complete` fixture wording after the contract advanced to `Phases 0 through 6 complete`. The post-closure repair is recorded in `EXP-0032.md`; the repair commit is `bf29cecda485adb2d7c55744e4692d1cf984e0a2`, and exact-head CI run `31867111333` succeeded with the required `validate` job successful.

Phase 6 is CLOSED. Phase 7 (`Full Pre-Release Gate and Release-PR Preparation`) remains `Planned` and owns the full pre-release gate. This evaluation does not pre-certify any current Build future validation, commit, push, CI, Phase 7 completion, PR, merge, tag, or release.
