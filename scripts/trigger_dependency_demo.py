#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dependency_demo.webhook import event_body, github_style_signature

SOURCE = "jira-direct"
EVENT = "dependency:requested"
DEFAULT_HOST = "https://app.replicated.rajistics.com"


def request_json(request: Request) -> dict:
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
            return json.loads(body) if body else {}
    except HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"API returned {exc.code}: {body}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue_key")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--host", default=os.getenv("OPENHANDS_HOST_RAJISTICS", DEFAULT_HOST))
    args = parser.parse_args()

    if not re.fullmatch(r"KAN-\d+", args.issue_key):
        raise SystemExit("issue key must match KAN-<number>")
    if not args.apply:
        print(json.dumps({"issue_key": args.issue_key, "event": EVENT, "source": SOURCE}, indent=2))
        return 0

    jira_base = os.getenv("JIRA_API_BASE_URL", "").rstrip("/")
    jira_token = os.getenv("JIRA_API_TOKEN")
    api_key = os.getenv("OPENHANDS_API_KEY_ORG")
    webhook_secret = os.getenv("JIRA_WEBHOOK_SECRET")
    if not all((jira_base, jira_token, api_key, webhook_secret)):
        raise SystemExit(
            "JIRA_API_BASE_URL, JIRA_API_TOKEN, OPENHANDS_API_KEY_ORG, and "
            "JIRA_WEBHOOK_SECRET are required for --apply"
        )

    fields = urlencode({"fields": "summary,description,labels,issuetype,project"})
    issue = request_json(
        Request(
            f"{jira_base}/rest/api/3/issue/{args.issue_key}?{fields}",
            headers={"Authorization": f"Bearer {jira_token}", "Accept": "application/json"},
        )
    )
    issue_fields = issue["fields"]
    if issue_fields["project"]["key"] != "KAN":
        raise SystemExit("issue must be in KAN")
    if issue_fields["issuetype"]["name"] != "Task":
        raise SystemExit("issue type must be Task")
    if "dependency-remediation" not in issue_fields.get("labels", []):
        raise SystemExit("issue must have dependency-remediation label")

    host = args.host.rstrip("/")
    auth = {"Authorization": f"Bearer {api_key}"}
    listing = request_json(Request(f"{host}/api/automation/v1?limit=100", headers=auth))
    automations = listing.get("automations", listing.get("items", listing))
    matching = [
        automation
        for automation in automations
        if automation.get("enabled")
        and automation.get("trigger", {}).get("source") == SOURCE
        and automation.get("trigger", {}).get("on") == EVENT
    ]
    if len(matching) != 1 or matching[0]["name"] != "Dependency Demo - Jira Snyk Remediation":
        raise SystemExit(f"expected only the enabled dependency demo automation, found {len(matching)}")

    webhook_listing = request_json(
        Request(f"{host}/api/automation/v1/webhooks", headers=auth)
    )
    webhooks = webhook_listing.get("webhooks", webhook_listing.get("items", webhook_listing))
    webhook_matches = [webhook for webhook in webhooks if webhook["source"] == SOURCE]
    if len(webhook_matches) != 1 or not webhook_matches[0].get("enabled"):
        raise SystemExit("expected one enabled jira-direct webhook")

    body = event_body(issue)
    result = request_json(
        Request(
            webhook_matches[0]["webhook_url"],
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature": github_style_signature(webhook_secret, body),
            },
            method="POST",
        )
    )
    print(json.dumps({"automation": matching[0]["id"], "event": EVENT, "issue_key": args.issue_key, "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
