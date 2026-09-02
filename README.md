# OpenHands Jira dependency remediation demo

A fast, controlled demonstration of OpenHands Enterprise turning a Snyk-style Maven finding in Jira into a validated draft pull request.

The demo uses a sanitized report fixture and a synthetic Log4Shell dependency version. It is intentionally small enough to complete in under ten minutes and does not call Snyk, exploit a target, or auto-merge code.

Created by an OpenHands AI agent on behalf of Rajiv Shah.

## Story

```text
Snyk-style report in Jira
→ approved manual event
→ OpenHands reproduces one finding
→ Maven property upgraded
→ tests, lint, and scanner pass
→ draft PR opened
→ evidence returned to Jira
```

## Safety model

- `main` is clean at Log4j `2.17.1`.
- `demo/log4j` contains the controlled `2.14.1` finding.
- Fix branches target `demo/log4j`, never `main`.
- The automation is independent of the existing command-injection demo and uses the unique `dependency:requested` event.
- Human review and merge are mandatory.

## Local validation

```bash
uv sync --locked --all-groups
uv run pytest -q
uv run ruff check .
uv run python scripts/run_dependency_scan.py --expect 0
```

See [`docs/demo-runbook.md`](docs/demo-runbook.md) for production registration, triggering, evidence, and fallback steps.
