# Dependency remediation demo runbook

## Purpose

Demonstrate Jira-driven remediation of a Snyk-style Maven finding in under ten minutes without changing the existing SAST automation or repository.

## Independent resources

- Repository: `rajshah4/openhands-dependency-remediation-demo`
- Clean branch: `main`
- Vulnerable branch: `demo/log4j`
- Event: `jira:issue_created`
- Jira contract: KAN Task with label `dependency-remediation`
- Automation: `Dependency Demo - Jira Snyk Remediation`

The command-injection repository and `Security Demo - Jira SAST Remediation` automation remain an unchanged fallback.

## Registration

The customer-safe preset is already registered as automation `19946faf-721e-496a-afb4-0944d2fe98e0`. Do not run the registration script during normal rehearsal; doing so would create a duplicate. Use `scripts/register_automation.py` only to replace a deleted automation.

## Validated remediation baseline

On September 2, 2026, the customer-safe remediation path completed in 3 minutes 36 seconds:

- Jira: [KAN-171](https://rajiv-shah.atlassian.net/browse/KAN-171)
- Draft PR: [#3](https://github.com/rajshah4/openhands-dependency-remediation-demo/pull/3)
- OpenHands conversation: [1115ff24-5de1-452d-be94-4b2ae6e75861](https://app.replicated.rajistics.com/conversations/1115ff24-5de1-452d-be94-4b2ae6e75861)
- CI: successful
- PR diff: `pom.xml` only
- Dependency automation state after rehearsal: enabled

On September 3, 2026, routing changed from a manual signed event to the filtered Jira issue-created event. The prompt, repository policy, and remediation behavior did not change.


The customer-facing automation prompt contains no scenario-specific package, branch, CVE, or version values; those controls live in repository policy and the scanner evidence.

## Rehearsal

### 1. Pause the broad SDLC automation

Before creating the Jira Task, disable `SDLC_1 - Jira to PR` in the Rajistics Automations UI. It has an unfiltered `jira:issue_created` trigger and will otherwise launch alongside this demo. Do not change its definition.

### 2. Ensure the dependency automation is enabled

```bash
uv run python scripts/set_automation.py enable --apply
```

This command cannot modify the SDLC or SAST automations.

### 3. Create a fresh Jira Task

```bash
uv run python scripts/create_demo_jira_ticket.py --apply
```

Creation automatically launches the dependency automation when the new issue is a KAN Task labeled `dependency-remediation`. No second trigger is required.

### 4. Restore SDLC and confirm the run

Restore `SDLC_1 - Jira to PR` to its previous enabled state immediately after the ticket is created. In Rajistics, open `Dependency Demo - Jira Snyk Remediation` and confirm a new run appears for the new Jira key.

For backfill only, `scripts/trigger_dependency_demo.py` can replay an issue-created payload. Keep every other enabled `jira:issue_created` automation paused before using it.

### 5. Narrate the evidence

Show:

1. Jira report context and acceptance criteria.
2. Initial normalized finding: Log4j `2.14.1`, CVE-2021-44228, count one.
3. Repository-owned dependency-remediation skill.
4. Minimal `pom.xml` change to `2.17.1`.
5. Tests, Ruff, and final finding count zero.
6. Draft PR targeting `demo/log4j`.
7. Jira comment linking the PR, CI, and exact OpenHands conversation.

### 6. Optionally disable the dependency automation

```bash
uv run python scripts/set_automation.py disable --apply
```

Leave it enabled only when you want labeled Jira Task creation to launch remediation automatically. Confirm the SDLC automation has been restored to its pre-demo state.

## Ten-minute pacing

- 0:00–1:00: create the Jira Task from the Snyk-style report
- 1:00–2:00: automatic conversation start
- 2:00–6:00: reproduce, inspect, and remediate
- 6:00–8:00: tests, lint, and clean rescan
- 8:00–10:00: PR and Jira evidence

If the finding does not reproduce within two minutes, stop and use the existing validated SAST demo rather than troubleshooting live.

## Reset

Do not merge a remediation PR. For another run, create a fresh Jira Task and let the agent create a Jira-linked fix branch from unchanged `demo/log4j`.

## Positioning

The fixture stands in for a report delivered by email, file share, or polling. Snyk remains the detection and policy system of record; OpenHands performs repository-aware remediation and evidence generation inside the customer environment.
