from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SPEC_FIELDS = {
    "enabled",
    "keep_alive",
    "model",
    "name",
    "repos",
    "template",
    "timeout",
    "trigger",
}


def load_prompt_automation(spec_path: Path) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text())
    payload = {key: value for key, value in spec.items() if key in SPEC_FIELDS}
    payload["prompt"] = (spec_path.parent / spec["prompt_file"]).read_text()
    return payload
