from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def event_body(issue: dict[str, Any]) -> bytes:
    payload = {
        "issue": issue,
        "webhookEvent": "jira:issue_created",
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()


def github_style_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"
