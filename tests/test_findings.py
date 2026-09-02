from pathlib import Path

import pytest

from dependency_demo.findings import (
    LOG4J_CORE,
    load_report,
    maven_property,
    normalize_findings,
    scan,
    version_tuple,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "security/reports/snyk-log4shell.json"


def test_clean_pom_has_no_findings() -> None:
    result = scan(ROOT / "pom.xml", REPORT)

    assert result["finding_count"] == 0
    assert result["findings"] == []


def test_vulnerable_pom_has_one_normalized_finding(tmp_path: Path) -> None:
    vulnerable_pom = tmp_path / "pom.xml"
    vulnerable_pom.write_text((ROOT / "pom.xml").read_text().replace("2.17.1", "2.14.1"))

    result = scan(vulnerable_pom, REPORT)

    assert result["finding_count"] == 1
    finding = result["findings"][0]
    assert finding == {
        "cves": ["CVE-2021-44228"],
        "cwes": ["CWE-502"],
        "ecosystem": "maven",
        "fingerprint": "28ea73de308a2571",
        "fixed_version": "2.17.1",
        "id": "SNYK-JAVA-ORGAPACHELOGGINGLOG4J-2314720",
        "installed_version": "2.14.1",
        "package": LOG4J_CORE,
        "severity": "CRITICAL",
        "title": "Remote Code Execution in Apache Log4j",
        "type": "open-source-vulnerability",
    }


def test_report_is_sanitized_snyk_shape() -> None:
    report = load_report(REPORT)

    assert report["ok"] is False
    assert report["vulnerabilities"][0]["packageName"] == LOG4J_CORE


def test_maven_property_requires_declared_property(tmp_path: Path) -> None:
    pom = tmp_path / "pom.xml"
    pom.write_text("<project xmlns='http://maven.apache.org/POM/4.0.0'/>")

    with pytest.raises(ValueError, match="missing Maven property"):
        maven_property(pom, "log4j2.version")


def test_version_tuple_rejects_non_numeric_version() -> None:
    with pytest.raises(ValueError, match="unsupported version"):
        version_tuple("2.17.1-SNAPSHOT")


def test_normalizer_ignores_unrelated_package() -> None:
    report = load_report(REPORT)
    report["vulnerabilities"][0]["packageName"] = "example:unrelated"

    assert normalize_findings(report, "2.14.1") == []
