#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dependency_demo.automation import load_prompt_automation

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "automations/jira/dependency-remediation/automation.prompt-preset.json"
SAMPLE_EVENT = ROOT / "tests/fixtures/jira-dependency-requested.json"
DEFAULT_HOST = "https://app.replicated.rajistics.com"


def post_json(url: str, api_key: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            return response.status, json.loads(response.read())
    except HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"OpenHands API returned {exc.code}: {body}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--host", default=os.getenv("OPENHANDS_HOST_RAJISTICS", DEFAULT_HOST))
    parser.add_argument("--spec", type=Path, default=SPEC)
    parser.add_argument("--sample-event", type=Path, default=SAMPLE_EVENT)
    args = parser.parse_args()

    payload = load_prompt_automation(args.spec)
    validation = {
        "endpoint": "/v1/preset/prompt",
        "draft": payload,
        "sampleEvent": json.loads(args.sample_event.read_text()),
    }
    if not args.apply:
        print(json.dumps(validation, indent=2))
        return 0

    api_key = os.getenv("OPENHANDS_API_KEY_ORG")
    if not api_key:
        raise SystemExit("OPENHANDS_API_KEY_ORG is required for --apply")

    host = args.host.rstrip("/")
    _, validation_result = post_json(
        f"{host}/api/automation/v1/validate", api_key, validation
    )
    if not validation_result.get("valid"):
        print(json.dumps(validation_result, indent=2))
        return 1

    status, result = post_json(
        f"{host}/api/automation/v1/preset/prompt", api_key, payload
    )
    output = {
        "enabled": result.get("enabled"),
        "id": result.get("id"),
        "name": result.get("name"),
        "status": status,
    }
    print(json.dumps(output, indent=2))
    (ROOT / "jira-automation-registration-results.json").write_text(
        json.dumps(output, indent=2) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
