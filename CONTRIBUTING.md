# Contributing to NudgeWhen

Thank you for your interest in NudgeWhen. This document explains how to contribute effectively to a very early-stage experimental project.

## Current state of the project

NudgeWhen is in the early stages of an open-source release train. At this phase:

- There is no Android application code, no Gradle build, no test suite, no CI workflow, no published release, and no installation procedure.
- The repository currently contains project documentation, an agentic-workflow experiment record, and the community-health files for the current phase.
- A single maintainer reviews contributions.
- The community-health files (`README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`) are the primary artefacts of this phase.

Application-code contribution instructions are conditional on application code existing later. They are not provided here.

## What is useful right now

The following contributions are useful at this stage:

- Documentation improvements: clearer wording, better organization, corrected typos, expanded explanations.
- Design discussion: contextual-reminder scenarios, voice-first and local-first considerations, accessibility considerations.
- Community-file improvements: the issue forms, the pull-request template, this contributing guide, the code of conduct, and the security policy.
- Use cases: realistic situations where a voice-first, local-first contextual reminder would help.
- Narrowly scoped proposals: small, focused changes that can be reviewed quickly.

The following contributions are not yet applicable:

- Android source code, Gradle changes, manifest changes, or resource changes.
- Test code.
- CI workflow changes.
- OpenCode governance changes (for example, `AGENTS.md` or `opencode.json`).
- Release automation.

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

External contributors should open pull requests from a topic branch against the current release branch (`release/v0.1.0` at the time of writing). The maintainer will review and decide whether to merge. There is no guaranteed review time and no guaranteed acceptance.

## Validation

Validation expectations depend on what currently exists:

- For documentation-only changes, re-read the affected files and verify that the Markdown renders correctly. There is no automated Markdown linter required at this stage.
- For community-file changes, re-read the affected files and verify the YAML or Markdown parses.
- For any change that affects links, verify that the relative links resolve to existing files.
- Do not claim validation that did not occur. If a check is not applicable at this stage, say so.

Application-code validation, test runs, and CI runs are not applicable at this stage because they do not exist yet.

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
