from dependency_demo.jira import DISCLOSURE, demo_issue_fields, jira_comment


def test_demo_issue_has_unique_task_contract() -> None:
    fields = demo_issue_fields()

    assert fields["project"] == {"key": "KAN"}
    assert fields["issuetype"] == {"name": "Task"}
    assert fields["labels"] == ["dependency-remediation"]
    assert fields["summary"].startswith("[SNYK]")


def test_issue_and_comment_include_ai_disclosure() -> None:
    issue_text = [
        node["content"][0]["text"]
        for node in demo_issue_fields()["description"]["content"]
    ]
    comment_text = [node["content"][0]["text"] for node in jira_comment("Evidence")["body"]["content"]]

    assert issue_text[-1] == DISCLOSURE
    assert comment_text[-1] == DISCLOSURE
