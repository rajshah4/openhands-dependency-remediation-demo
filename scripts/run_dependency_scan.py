#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dependency_demo.findings import scan

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "security/reports/snyk-log4shell.json"
DEFAULT_OUTPUT = ROOT / "security/findings/generated-dependency-report.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect", type=int)
    parser.add_argument("--pom", type=Path, default=ROOT / "pom.xml")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = scan(args.pom, args.report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Dependency findings: {result['finding_count']}")
    print(f"Normalized report: {args.output}")

    if args.expect is not None and result["finding_count"] != args.expect:
        print(f"Expected {args.expect} findings")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
