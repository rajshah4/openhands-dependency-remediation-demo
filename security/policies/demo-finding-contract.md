# Controlled repository finding contract

This repository adapter constrains the broad security-remediation workflow to one deterministic test fixture. These values are demo data, not reusable skill policy.

The repository accepts exactly one normalized finding with these values:

```json
{
  "id": "SNYK-JAVA-ORGAPACHELOGGINGLOG4J-2314720",
  "type": "open-source-vulnerability",
  "ecosystem": "maven",
  "package": "org.apache.logging.log4j:log4j-core",
  "installed_version": "2.14.1",
  "fixed_version": "2.17.1",
  "severity": "CRITICAL",
  "cves": ["CVE-2021-44228"],
  "cwes": ["CWE-502"]
}
```

The repository scanner derives the installed version from `pom.xml`; report text cannot override it. Stop if the ID, package, installed version, safe version, or finding count differs.
