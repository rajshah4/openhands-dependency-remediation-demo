import json

from dependency_demo.webhook import event_body, github_style_signature


def test_event_body_is_stable_and_scoped() -> None:
    body = event_body({"key": "KAN-999", "fields": {"labels": ["dependency-remediation"]}})
    payload = json.loads(body)

    assert payload["webhookEvent"] == "dependency:requested"
    assert payload["issue"]["key"] == "KAN-999"


def test_signature_uses_github_style_sha256() -> None:
    assert github_style_signature("secret", b"body") == (
        "sha256=dc46983557fea127b43af721467eb9b3fde2338fe3e14f51952aa8478c13d355"
    )
