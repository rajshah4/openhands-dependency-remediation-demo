import json
from pathlib import Path

from dependency_demo.automation import load_prompt_automation

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "automations/jira/dependency-remediation/automation.prompt-preset.json"
SKILL = ROOT / ".agents/skills/security-remediation/SKILL.md"


def test_prompt_automation_is_isolated_and_disabled() -> None:
    payload = load_prompt_automation(SPEC)

    assert payload["name"] == "Dependency Demo - Jira Snyk Remediation"
    assert payload["enabled"] is False
    assert payload["timeout"] == 600
    assert payload["trigger"]["source"] == "jira-direct"
    assert payload["trigger"]["on"] == "jira:issue_created"
    assert payload["repos"] == [
        {
            "url": "https://github.com/rajshah4/openhands-dependency-remediation-demo",
            "ref": "demo/log4j",
        }
    ]


def test_prompt_is_loaded_from_file() -> None:
    payload = load_prompt_automation(SPEC)

    assert "# Jira-driven security remediation" in payload["prompt"]
    assert "prompt_file" not in payload


def test_security_remediation_skill_is_reusable() -> None:
    skill = SKILL.read_text()

    assert "name: security-remediation" in skill
    assert "software composition analysis" in skill
    assert "Open-source license policy" in skill
    assert "Static application security testing" in skill
    assert "Dynamic application security testing" in skill
    assert "Stop without editing or opening a pull request" in skill
    assert "Never approve, merge, dismiss findings" in skill
    for scenario_detail in (
        "Log4Shell",
        "Log4j",
        "SNYK-JAVA-ORGAPACHELOGGINGLOG4J-2314720",
        "2.14.1",
        "2.17.1",
        "demo/log4j",
        "under ten minutes",
    ):
        assert scenario_detail not in skill


def test_customer_facing_prompt_contains_no_scenario_specific_fix() -> None:
    prompt = load_prompt_automation(SPEC)["prompt"]

    assert "2.14.1" not in prompt
    assert "2.17.1" not in prompt
    assert "demo/log4j" not in prompt
    assert "CVE-2021-44228" not in prompt
    assert "log4j" not in prompt.lower()


def test_sample_event_matches_filter_contract() -> None:
    event = json.loads((ROOT / "tests/fixtures/jira-issue-created.json").read_text())

    assert event["webhookEvent"] == "jira:issue_created"
    assert event["issue"]["fields"]["project"]["key"] == "KAN"
    assert event["issue"]["fields"]["issuetype"]["name"] == "Task"
    assert "dependency-remediation" in event["issue"]["fields"]["labels"]
