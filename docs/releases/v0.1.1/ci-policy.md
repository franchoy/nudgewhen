# CI Policy — NudgeWhen v0.1.1

**Document status:** Phase 2A local candidate — `v0.1.1` persistent CI policy
**Active release:** `v0.1.1`
**Active release branch:** `release/v0.1.1`
**Workflow file:** `.github/workflows/ci.yml`

## Purpose and scope

This document records the persistent CI policy that replaces the one-release-only CI configuration produced for `v0.1.0`. The policy governs the GitHub Actions CI workflow used by future release branches, pull requests targeting `main`, pushes to `main`, and manual dispatches.

The policy is local repository evidence. It records the intended trigger matrix, the stable job name, the security posture, the validation behavior, and the explicit boundary that remote main protection and ruleset verification are not performed in Phase 2A and remain pending evidence for Phase 2B.

This document is the v0.1.1 Phase 2A deliverable. It is not a remote configuration. It does not modify any GitHub branch protection, ruleset, secret, or repository setting. Remote settings are independently read back and recorded in a later Phase 2B task.

## Trigger matrix

The CI workflow at `.github/workflows/ci.yml` runs on the following events:

- **`push` to any `release/**` branch** — every push to any release branch under the `release/` namespace starts the workflow.
- **`pull_request` targeting `main`** — every pull request opened against the `main` branch starts the workflow on the pull request ref.
- **`push` to `main`** — every push to the `main` branch starts the workflow on the merged commit.
- **`workflow_dispatch`** — the workflow can be started manually from the GitHub Actions tab for ad hoc validation.

The trigger matrix covers all four required events and is independent of any single release version. The CI configuration is no longer tied to `release/v0.1.0`.

## Stable required job name

The CI workflow defines exactly one job. The job name is `validate`. The `name:` field on the job is also `validate`. Branch protection or ruleset configuration on `main` can require the stable `validate` check by name without being tied to a single release version.

The job identity, step names, and step ordering are part of the stable job contract and are not changed by this policy.

## Security posture

The CI workflow applies the following security controls:

- **Read-only default permissions.** The workflow sets `permissions: contents: read` at the top level. No job or step is granted additional write permissions. The workflow cannot push, publish, create tags, modify repository settings, or interact with releases.
- **Full-SHA action pinning.** Every `uses:` reference in the workflow pins a third-party action to a full commit SHA with a trailing version comment (for example, `actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0`). The full-SHA form is preserved and is not replaced with mutable tag or branch references.
- **Bounded timeout.** The `validate` job sets `timeout-minutes: 30`. The workflow cannot run indefinitely.
- **Concurrency cancellation.** The workflow sets `concurrency.group: ${{ github.workflow }}-${{ github.ref }}` and `concurrency.cancel-in-progress: true`. Superseded runs on the same ref are cancelled; CI does not accumulate stale runs.
- **No secrets or release publication.** The workflow does not reference any secret, does not sign or upload a release artifact, does not create or push a tag, and does not publish a GitHub release. The debug APK is uploaded as a workflow artifact only.

The security posture is preserved from the v0.1.0 baseline and generalized to all release branches. No new permission, secret, or external integration is added.

## Validation behavior

Repository validation runs through the existing local validation entry point at `./scripts/validate-local.sh`. The `validate-local` step executes `./scripts/validate-local.sh --require-clean` as the repository-side validation command. The same script is documented in `docs/local-validation.md` and is the supported validation entry point for the v0.1.0 local-validation baseline carried forward into v0.1.1.

The local validation command behavior is not weakened. The `--require-clean` flag is preserved. The required, docs, android, and skip-android groups documented in `docs/local-validation.md` remain the supported invocation surface.

The debug APK upload remains an artifact of successful validation only. The `upload-debug-apk` step uses `if: success()` and only runs when every preceding step in the `validate` job completes successfully. The upload is performed with `actions/upload-artifact` pinned to a full commit SHA. The artifact is named `app-debug-apk`, sourced from `app/build/outputs/apk/debug/app-debug.apk`, and retained for 14 days. The upload is not a release publication.

No production signing or store publication is performed. The debug APK is the only artifact and is unsigned. The workflow does not sign the APK, does not create a release, and does not upload to an app store or distribution service.

## Branch protection and ruleset status

Remote GitHub branch protection, ruleset configuration, and status-check enforcement on `main` are explicitly out of scope for Phase 2A. This Build does not perform any network command, does not call `gh`, does not read the remote `main` protection or ruleset state, and does not modify any remote setting.

The following items are Phase 2B pending evidence, not Phase 2A completed evidence:

- Whether `main` is currently protected by a branch protection rule.
- Whether a ruleset applies to `main`.
- Whether the ruleset requires the stable `validate` status check.
- Whether the ruleset requires a pull request before merge.
- Whether force pushes to `main` are blocked.
- Whether deletion of `main` is blocked.
- Whether the actual `validate` job name is the exact required check identifier in the ruleset.
- Any other remote configuration that depends on a live readback.

No claim is made in this document, in the workflow file, in the Phase 2 phase-list, or in the Phase 2A experiment record that `main` already requires the `validate` check. The claim that `main` requires `validate` depends on independently reading back the remote configuration in Phase 2B and is not established by the local workflow file alone.

## Release-train status

Phase 2A produces a local repository candidate only. The candidate consists of:

- the generalized `.github/workflows/ci.yml`;
- this CI policy document;
- the synchronized Phase 2 status and validation checklist in `docs/releases/v0.1.1/phase-list.md`;
- the new `docs/agentic-development/experiments/EXP-0020.md` evidence record.

The following actions remain separate repository or external actions and are not part of Phase 2A:

- staging the Phase 2A candidate paths;
- committing the Phase 2A candidate paths on `release/v0.1.1`;
- pushing the Phase 2A candidate paths to the remote `release/v0.1.1`;
- the resulting `validate` workflow run on the pushed commit;
- remote main protection or ruleset readback;
- the maintainer acceptance of the Phase 2A candidate.

No claim is made that the Phase 2A candidate is committed, pushed, or running on the remote. No claim is made that the remote `main` branch is protected or that the `validate` check is required by the ruleset. Both categories of claim depend on future, separately authorized actions and on the Phase 2B remote readback.

## Cross-references

- Active phase list: [phase-list.md](./phase-list.md)
- Active release charter: [release-charter.md](./release-charter.md)
- Active `AGENTS.md`: [../../../AGENTS.md](../../../AGENTS.md)
- Local validation documentation: [../../local-validation.md](../../local-validation.md)
- Phase 2A experiment record: [../../agentic-development/experiments/EXP-0020.md](../../agentic-development/experiments/EXP-0020.md)
- CI workflow file: [../../../.github/workflows/ci.yml](../../../.github/workflows/ci.yml)
