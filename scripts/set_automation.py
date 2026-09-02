#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

NAME = "Dependency Demo - Jira Snyk Remediation"
DEFAULT_HOST = "https://app.replicated.rajistics.com"


def request_json(request: Request) -> dict:
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"OpenHands API returned {exc.code}: {body}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", choices=("enable", "disable"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--host", default=os.getenv("OPENHANDS_HOST_RAJISTICS", DEFAULT_HOST))
    args = parser.parse_args()

    api_key = os.getenv("OPENHANDS_API_KEY_ORG")
    if not api_key:
        raise SystemExit("OPENHANDS_API_KEY_ORG is required")
    host = args.host.rstrip("/")
    headers = {"Authorization": f"Bearer {api_key}"}
    listing = request_json(Request(f"{host}/api/automation/v1?limit=100", headers=headers))
    automations = listing.get("automations", listing.get("items", listing))
    matches = [automation for automation in automations if automation["name"] == NAME]
    if len(matches) != 1:
        raise SystemExit(f"expected one {NAME!r} automation, found {len(matches)}")

    automation = matches[0]
    desired = args.state == "enable"
    plan = {"id": automation["id"], "name": NAME, "from": automation["enabled"], "to": desired}
    if not args.apply:
        print(json.dumps(plan, indent=2))
        return 0

    body = json.dumps({"enabled": desired}).encode()
    result = request_json(
        Request(
            f"{host}/api/automation/v1/{automation['id']}",
            data=body,
            headers={**headers, "Content-Type": "application/json"},
            method="PATCH",
        )
    )
    print(json.dumps({"id": result["id"], "name": result["name"], "enabled": result["enabled"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
