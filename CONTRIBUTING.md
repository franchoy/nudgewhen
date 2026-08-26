# Contributing to NudgeWhen

Thank you for your interest in NudgeWhen. This document explains how to contribute effectively to a very early-stage experimental project.

## Current state of the project

NudgeWhen is an early-stage experimental open-source Android project. At this phase:

- The `v0.1.0` release is complete and historical; see `docs/releases/v0.1.0/` for its record.
- The active in-progress release is `v0.1.2`, developed on the `release/v0.1.2` branch.
- The repository contains Android source, Gradle build files, a manifest and resources, documentation, agentic-workflow experiment records, and community-health files.
- A single maintainer reviews contributions.
- There is no production-readiness or support guarantee; this is experimental software.

Android source, Gradle, manifest, resources, validation, and CI artefacts now exist in the repository. Contribution instructions for them are below.

## Branches and pull-request targets

External contributors should work on a topic branch and target the current release branch. The durable convention is `release/vX.Y.Z`; the current binding is `release/v0.1.2`. The historical `release/v0.1.0` and `release/v0.1.1` branches remain in the repository as evidence of the completed releases and are not the current target for new work. The maintainer reviews and decides whether to merge; there is no guaranteed review time and no guaranteed acceptance.

## What is useful right now

The following contributions are useful at this stage when they are explicitly scoped and discussed in an issue first:

- Documentation improvements: clearer wording, better organization, corrected typos, expanded explanations.
- Design discussion: contextual-reminder scenarios, voice-first and local-first considerations, accessibility considerations.
- Community-file improvements: the issue forms, the pull-request template, this contributing guide, the code of conduct, and the security policy.
- Use cases: realistic situations where a voice-first, local-first contextual reminder would help.
- Narrowly scoped code changes: small, focused changes to Android source, Gradle, manifest, or resources that can be reviewed quickly.
- Validation improvements: small, focused changes to local validation scripts or validation documentation that can be reviewed quickly.
- CI-related changes: small, focused changes to continuous integration workflow files.
- Release-process improvements: small, focused changes to release automation or release documentation.

## Issue-first discussion

For any non-trivial change, open an issue first and reach agreement with the maintainer before opening a pull request. A focused issue describing the problem, the proposed change, and the expected outcome helps the maintainer review the proposal and avoids wasted effort.

Search existing issues first. A proposal that duplicates an open or recently closed issue is unlikely to be accepted.

## Pull requests

Pull requests should be:

- Small and focused on a single concern.
- Clearly described: what changed, why, and what was validated.
- Truthful: do not claim validation that did not occur.
- Self-contained: do not include unrelated changes, reformatting, or drive-by modifications.
- Linked to the relevant issue when one exists.

External contributors should open pull requests from a topic branch against the current release branch (`release/v0.1.2` at the time of writing). The maintainer will review and decide whether to merge. There is no guaranteed review time and no guaranteed acceptance. Ordinary release work does not target `main` early; only after the release phases and the full pre-release gate are complete does the maintainer open the release-bearing PR from the release branch to `main`.

## Validation

Validation guidance depends on the authorized scope of the change:

- The local validation suite is `./scripts/validate-local.sh`. It is the sanctioned entry point for the validation groups defined by the project.
- For documentation-only changes, focused readback of the affected files and verification that relative links resolve to existing files may be used when that is the authorized scope.
- For broader code, validator, or Android changes, the appropriate local validation group or the full suite must be run when authorized.
- Do not claim validation that did not occur. If a check was not run as part of the authorized scope, say so.

## Commit messages

There is no strict commit-message convention at this stage. A short descriptive message is sufficient. The maintainer may rewrite commit messages during integration.

## Licensing of contributions

By submitting a contribution, you agree to license it under the Apache License 2.0. No contributor license agreement or copyright assignment is required or implied. The full license text is in `LICENSE`.

## AI-assisted contributions

AI-assisted contributions are permitted. The contributor must:

- Disclose material AI assistance in the pull request description.
- Personally review the entire contribution before submission, including any AI-generated text, code, or suggestions.
- Take full responsibility for the submitted work.

AI-generated contributions are not exempt from review. The maintainer reviews all contributions on their merit.

## Prohibited content

Do not commit any of the following:

- Secrets, credentials, tokens, or private keys of any kind.
- Generated credentials or test fixtures containing real-looking credentials.
- Personal paths, machine names, or other identifying infrastructure details.
- Raw agent transcripts or session exports.
- Personal email addresses as evidence or content.

If a contribution requires an example, use clearly synthetic placeholder values.

## Security vulnerabilities

Do not file security vulnerabilities as public issues. Use the reporting route described in `SECURITY.md`.

## Code of conduct

All contributors are expected to follow the project code of conduct, which is in `CODE_OF_CONDUCT.md`.

## No service-level promise

This is a single-maintainer experimental project. There is no guaranteed review time, no guaranteed response time, and no guaranteed acceptance of any contribution. The maintainer may decline, defer, or substantially revise a contribution at their sole discretion.

## Related documents

- [README.md](README.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [LICENSE](LICENSE)
