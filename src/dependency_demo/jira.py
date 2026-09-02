from __future__ import annotations

from typing import Any

DISCLOSURE = "Created by an OpenHands AI agent on behalf of Rajiv Shah."


def adf_document(paragraphs: list[str]) -> dict[str, Any]:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": paragraph}],
            }
            for paragraph in paragraphs
        ],
    }


def demo_issue_fields(project: str = "KAN") -> dict[str, Any]:
    return {
        "project": {"key": project},
        "issuetype": {"name": "Task"},
        "summary": "[SNYK] Upgrade Log4j in trade audit service",
        "labels": ["dependency-remediation"],
        "description": adf_document(
            [
                "Repository: rajshah4/openhands-dependency-remediation-demo",
                "Branch: demo/log4j",
                "Scanner: Snyk report fixture",
                "Report: security/reports/snyk-log4shell.json",
                "Finding ID: SNYK-JAVA-ORGAPACHELOGGINGLOG4J-2314720",
                "Package: org.apache.logging.log4j:log4j-core",
                "Installed version: 2.14.1",
                "Fixed version: 2.17.1",
                "CVE: CVE-2021-44228",
                (
                    "Acceptance: reproduce one critical finding, update only the Maven "
                    "Log4j property, run tests and lint, reduce the finding count to zero, "
                    "and open a draft pull request targeting demo/log4j."
                ),
                "OpenHands must not merge or approve the pull request.",
                DISCLOSURE,
            ]
        ),
    }


def jira_comment(text: str) -> dict[str, Any]:
    return {"body": adf_document([text, DISCLOSURE])}
