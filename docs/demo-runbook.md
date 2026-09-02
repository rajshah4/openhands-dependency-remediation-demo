# Dependency remediation demo runbook

## Purpose

Demonstrate Jira-driven remediation of a Snyk-style Maven finding in under ten minutes without changing the existing SAST automation or repository.

## Independent resources

- Repository: `rajshah4/openhands-dependency-remediation-demo`
- Clean branch: `main`
- Vulnerable branch: `demo/log4j`
- Event: `dependency:requested`
- Jira contract: KAN Task with label `dependency-remediation`
- Rehearsal issue: existing KAN-168
- Automation: `Dependency Demo - Jira Snyk Remediation`

The command-injection repository and `Security Demo - Jira SAST Remediation` automation remain an unchanged fallback.

## Registration

The customer-safe preset is already registered as automation `19946faf-721e-496a-afb4-0944d2fe98e0`. Do not run the registration script during normal rehearsal; doing so would create a duplicate. Use `scripts/register_automation.py` only to replace a deleted automation.

## Validated rehearsal

On September 2, 2026, the final customer-safe prompt completed the fresh-ticket workflow in 3 minutes 36 seconds:

- Jira: [KAN-171](https://rajiv-shah.atlassian.net/browse/KAN-171)
- Draft PR: [#3](https://github.com/rajshah4/openhands-dependency-remediation-demo/pull/3)
- OpenHands conversation: [1115ff24-5de1-452d-be94-4b2ae6e75861](https://app.replicated.rajistics.com/conversations/1115ff24-5de1-452d-be94-4b2ae6e75861)
- CI: successful
- PR diff: `pom.xml` only
- Dependency automation state after rehearsal: enabled

The customer-facing automation prompt contains no scenario-specific package, branch, CVE, or version values; those controls live in repository policy and the scanner evidence.

## Rehearsal

### 1. Pause the broad SDLC automation

Before creating the Jira Task, disable `SDLC_1 - Jira to PR` in the Rajistics Automations UI. It has an unfiltered `jira:issue_created` trigger and will otherwise launch alongside this demo. Do not change its definition, and restore its previous enabled state after the ticket is created.

### 2. Create a fresh Jira Task

```bash
ticket="$(uv run python scripts/create_demo_jira_ticket.py --apply)"
issue_key="$(jq -r .key <<<"$ticket")"
echo "$ticket"
```

This creates a uniquely labeled KAN Task containing the Snyk-style report context and acceptance criteria. Restore `SDLC_1 - Jira to PR` after creation.

### 3. Ensure the dependency automation is enabled

```bash
uv run python scripts/set_automation.py enable --apply
```

This command cannot modify the SDLC or SAST automations.

### 4. Start the approved manual event

```bash
uv run python scripts/trigger_dependency_demo.py "$issue_key" --apply
```

The script fetches the current Jira issue, validates project/type/label, confirms exactly one enabled automation matches `dependency:requested`, signs the event, and sends it to the existing verified webhook source.

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

Leave it enabled only when you want it ready for another signed manual event. Confirm the SDLC automation has been restored to its pre-demo state.

## Ten-minute pacing

- 0:00–1:00: Jira and Snyk-style report
- 1:00–2:00: signed manual trigger and conversation start
- 2:00–6:00: reproduce, inspect, and remediate
- 6:00–8:00: tests, lint, and clean rescan
- 8:00–10:00: PR and Jira evidence

If the finding does not reproduce within two minutes, stop and use the existing validated SAST demo rather than troubleshooting live.

## Reset

Do not merge a remediation PR. For another run, create a fresh Jira Task and let the agent create a Jira-linked fix branch from unchanged `demo/log4j`.

## Positioning

The fixture stands in for a report delivered by email, file share, or polling. Snyk remains the detection and policy system of record; OpenHands performs repository-aware remediation and evidence generation inside the customer environment.
