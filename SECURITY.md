# Security Policy

NudgeWhen is in an early experimental stage. This document explains how to report a suspected security vulnerability, what to expect, and what the project does and does not promise.

## Current state

NudgeWhen is an early experimental project. The current and historical release states are:

- `v0.1.0` is the historical released baseline. The published GitHub `v0.1.0` release, the merged `v0.1.0` release pull request, and the `v0.1.0` release branch exist as historical evidence and are not the active release train.
- `v0.1.1` is the active documentation, governance, validation, CI, supply-chain, workspace-hygiene, and release metadata hardening release train. It is developed on the single branch `release/v0.1.1`, which is the current state. The published `v0.1.1` release, the merged `v0.1.1` release pull request, and the annotated `v0.1.1` tag do not yet exist.
- A minimal Android application project exists, including Android source, Gradle build files, the Gradle wrapper, an Android manifest, Android resources, a GitHub Actions CI workflow, a local validation suite, and a locally generated debug APK at `app/build/outputs/apk/debug/app-debug.apk` (ignored and not committed).
- The released `v0.1.0` baseline contains no reminder, voice, speech, location, geofencing, notification, persistence, contextual-trigger, networking, analytics, telemetry, or background-service functionality. It is a static-screen Android technical baseline only. No production-readiness, stability, security, or compatibility guarantee is made.
- This document does not create a production support promise. There is no supported-version matrix at this stage. Supported-version guidance will be added when a releasable production-oriented version exists.

## Primary reporting route: GitHub private vulnerability reporting

GitHub private vulnerability reporting is enabled on this repository and is the primary route for reporting suspected security vulnerabilities. It submits the vulnerability privately to the repository maintainers.

To file a report:

1. Open the repository on GitHub.
2. Open the repository's **Security** area (sometimes labelled "Security and quality").
3. Select **Report a vulnerability**.
4. Complete and submit the private report.

This is the ordinary reporter workflow. It is distinct from the maintainer's draft-advisory workflow, which is not described here because it is not the reporter's route.

## Fallback route: minimal public issue requesting private contact

If GitHub private vulnerability reporting is not available for any reason, open a minimal public issue that requests a private contact route.

The issue body must contain only the request for private contact. It must NOT contain:

- Vulnerability details.
- Exploit steps.
- Reproduction steps.
- Proof of concept.
- Logs, stack traces, or screenshots.
- Personal data, credentials, or session identifiers.
- Affected component names, file paths, line numbers, or version strings.
- Any information that could be used to construct an exploit.

Sensitive material must not be filed as a normal public bug report.

## What to expect after a report

Reports are reviewed on a best-effort basis by the single project maintainer. The project does not promise:

- A response time.
- A remediation time.
- A coordinated-disclosure timeline or embargo length.
- CVE assignment.
- A bug bounty or any monetary award.
- A security audit or formal verification.
- A specific fix version or release date.
- Any other security guarantee.

## What the project does not have

The project does not currently have:

- A security audit.
- A bug bounty program.
- A published threat model.
- A signed release process.
- An out-of-band communication channel for security.
- Encryption guarantees beyond what the chosen platform provides.
- A privacy program.
- A production-readiness, stability, security, or compatibility guarantee.
- A supported-version matrix or a formal support channel.

## Ordinary non-security defects

Ordinary non-security defects (typos, broken links, missing documentation, application defects when an application exists) are reported through the bug-report issue form, not through the security-reporting route.

## Conduct reports are separate

Concerns about contributor behaviour are reported through the routes described in `CODE_OF_CONDUCT.md`, not through the security-reporting route.

## No invented contact channel

This document does not publish a personal email address. The reporting routes above are the only routes.

## Supported versions

There are no supported versions at this time. When a releasable version exists, this document will be updated to specify which versions receive security updates and on what basis.
