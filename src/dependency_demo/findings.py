from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

LOG4J_CORE = "org.apache.logging.log4j:log4j-core"
MAVEN_NAMESPACE = {"m": "http://maven.apache.org/POM/4.0.0"}


def version_tuple(version: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError as exc:
        raise ValueError(f"unsupported version: {version}") from exc


def maven_property(pom_path: Path, property_name: str) -> str:
    root = ElementTree.parse(pom_path).getroot()
    value = root.findtext(f"m:properties/m:{property_name}", namespaces=MAVEN_NAMESPACE)
    if not value:
        raise ValueError(f"missing Maven property: {property_name}")
    return value.strip()


def load_report(report_path: Path) -> dict[str, Any]:
    return json.loads(report_path.read_text())


def normalize_findings(report: dict[str, Any], installed_version: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for vulnerability in report.get("vulnerabilities", []):
        if vulnerability.get("packageName") != LOG4J_CORE:
            continue

        fixed_versions = vulnerability.get("fixedIn") or []
        if not fixed_versions:
            continue
        fixed_version = fixed_versions[0]
        if version_tuple(installed_version) >= version_tuple(fixed_version):
            continue

        finding_id = vulnerability["id"]
        fingerprint_input = f"{finding_id}|{LOG4J_CORE}|{installed_version}|{fixed_version}"
        findings.append(
            {
                "cves": vulnerability.get("identifiers", {}).get("CVE", []),
                "cwes": vulnerability.get("identifiers", {}).get("CWE", []),
                "ecosystem": "maven",
                "fingerprint": hashlib.sha256(fingerprint_input.encode()).hexdigest()[:16],
                "fixed_version": fixed_version,
                "id": finding_id,
                "installed_version": installed_version,
                "package": LOG4J_CORE,
                "severity": vulnerability.get("severity", "unknown").upper(),
                "title": vulnerability.get("title", "Dependency vulnerability"),
                "type": "open-source-vulnerability",
            }
        )
    return findings


def scan(pom_path: Path, report_path: Path) -> dict[str, Any]:
    installed_version = maven_property(pom_path, "log4j2.version")
    findings = normalize_findings(load_report(report_path), installed_version)
    try:
        source_report = report_path.resolve().relative_to(pom_path.resolve().parent).as_posix()
    except ValueError:
        source_report = report_path.name
    return {
        "finding_count": len(findings),
        "findings": findings,
        "scanner": "snyk",
        "source_report": source_report,
    }
