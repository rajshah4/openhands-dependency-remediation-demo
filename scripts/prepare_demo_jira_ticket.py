#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dependency_demo.jira import demo_issue_fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue_key")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not re.fullmatch(r"KAN-\d+", args.issue_key):
        raise SystemExit("issue key must match KAN-<number>")
    fields = demo_issue_fields()
    fields.pop("project")
    fields.pop("issuetype")
    payload = {"fields": fields}
    if not args.apply:
        print(json.dumps({"issue_key": args.issue_key, **payload}, indent=2))
        return 0

    base_url = os.getenv("JIRA_API_BASE_URL", "").rstrip("/")
    token = os.getenv("JIRA_API_TOKEN")
    site_url = os.getenv("JIRA_SITE_URL", "").rstrip("/")
    if not base_url or not token:
        raise SystemExit("JIRA_API_BASE_URL and JIRA_API_TOKEN are required for --apply")

    request = Request(
        f"{base_url}/rest/api/3/issue/{args.issue_key}",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="PUT",
    )
    try:
        with urlopen(request, timeout=30) as response:
            response.read()
    except HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"Jira API returned {exc.code}: {body}") from exc

    print(json.dumps({"key": args.issue_key, "url": f"{site_url}/browse/{args.issue_key}"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
