---
name: dependency-remediation
description: Remediate the controlled Snyk-style Log4Shell Maven finding in under ten minutes, then create an evidence-rich draft pull request and Jira update.
triggers:
  - dependency-remediation
  - snyk
  - maven
  - log4j
---

# Dependency remediation

Use this skill only for the controlled Jira Bug labeled `dependency-remediation`.

## Workflow

1. Read `AGENTS.md`, the Jira request, and `references/finding-contract.md`.
2. Confirm the branch is `demo/log4j` and the working tree is clean.
3. Reproduce the finding before editing:

   ```bash
   uv sync --locked --all-groups
   uv run python scripts/run_dependency_scan.py --expect 1
   ```

4. Confirm exactly one critical `SNYK-JAVA-ORGAPACHELOGGINGLOG4J-2314720` finding for `org.apache.logging.log4j:log4j-core` version `2.14.1`, fixed in `2.17.1`.
5. Create `fix/<jira-key>-log4j` from `demo/log4j`.
6. Change only the `log4j2.version` property in `pom.xml` from `2.14.1` to `2.17.1`. Do not alter the report fixture, parser, tests, or acceptance gate.
7. Run all validation from `AGENTS.md`; the final finding count must be zero.
8. Review the diff and confirm only `pom.xml` changed.
9. Commit, push, and open a draft PR targeting `demo/log4j`.
10. Include the Jira key, scanner, finding ID, CVE, package, before/after versions, before/after finding counts, validation results, residual risk, and exact conversation URL in the PR.
11. Verify the published PR contains the exact conversation URL and no placeholder.
12. Post the PR URL and evidence to Jira through `scripts/comment_jira.py`; verify the comment exists.
13. Finish within ten minutes. If the expected finding does not reproduce within two minutes, stop without changing code and report the mismatch.

## Human gate

Never merge or approve the pull request. Policy-based auto-merge is a future maturity step, not part of this demo.
