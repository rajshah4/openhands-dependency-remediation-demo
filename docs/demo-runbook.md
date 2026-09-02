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

## One-time registration

The preset is disabled by default.

```bash
set -a
source ~/Code/install_replicate/.env
set +a
uv run python scripts/register_automation.py --apply
```

## Rehearsal

### 1. Prepare the existing Jira Task

```bash
uv run python scripts/prepare_demo_jira_ticket.py KAN-168 --apply
```

This updates a pre-existing Task with the Snyk report context and label. It cannot emit Jira's issue-created event, so the enabled broad `SDLC_1 - Jira to PR` automation and the disabled SAST automation are not triggered.

### 2. Enable only the dependency automation

```bash
uv run python scripts/set_automation.py enable --apply
```

This command cannot modify the SDLC or SAST automations.

### 3. Start the approved manual event

```bash
uv run python scripts/trigger_dependency_demo.py KAN-### --apply
```

The script fetches the current Jira issue, validates project/type/label, confirms exactly one enabled automation matches `dependency:requested`, signs the event, and sends it to the existing verified webhook source.

### 4. Narrate the evidence

Show:

1. Jira report context and acceptance criteria.
2. Initial normalized finding: Log4j `2.14.1`, CVE-2021-44228, count one.
3. Repository-owned dependency-remediation skill.
4. Minimal `pom.xml` change to `2.17.1`.
5. Tests, Ruff, and final finding count zero.
6. Draft PR targeting `demo/log4j`.
7. Jira comment linking the PR, CI, and exact OpenHands conversation.

### 5. Disable the new automation

```bash
uv run python scripts/set_automation.py disable --apply
```

The existing automations should have the same enabled states and definitions they had before the rehearsal.

## Ten-minute pacing

- 0:00–1:00: Jira and Snyk-style report
- 1:00–2:00: signed manual trigger and conversation start
- 2:00–6:00: reproduce, inspect, and remediate
- 6:00–8:00: tests, lint, and clean rescan
- 8:00–10:00: PR and Jira evidence

If the finding does not reproduce within two minutes, stop and use the existing validated SAST demo rather than troubleshooting live.

## Reset

Do not merge a remediation PR. For another run, prepare KAN-168 again and let the agent create a unique `fix/KAN-168-log4j` branch, with a numeric suffix when needed, from unchanged `demo/log4j`.

## Positioning

The fixture stands in for a report delivered by email, file share, or polling. Snyk remains the detection and policy system of record; OpenHands performs repository-aware remediation and evidence generation inside the customer environment.
