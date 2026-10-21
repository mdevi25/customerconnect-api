
"""Validate AIDLC Command Center CSV structures."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "aidlc-control"

SCHEMAS = {
    "execution_plan.csv": [
        "work_id", "work_item", "dependency", "owner",
        "priority", "status", "readiness", "gate", "evidence",
    ],
    "risk_register.csv": [
        "risk_id", "work_id", "risk_description", "likelihood",
        "impact", "roam_status", "owner", "response_action",
        "readiness_impact", "evidence",
    ],
    "kpi_register.csv": [
        "kpi_id", "kpi_name", "scope", "target", "actual",
        "unit", "evidence", "measurement_status",
        "measurement_note",
    ],
    "approval_register.csv": [
        "approval_id", "artifact_id", "artifact_path",
        "artifact_version", "approver_role", "decision_status",
        "evidence_reference", "decision_date",
    ],
}


def validate_csv(filename, expected_columns):
    path = ROOT / filename

    if not path.is_file():
        return [f"{filename}: file missing"]

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != expected_columns:
            return [f"{filename}: incorrect columns or column order"]

        rows = list(reader)

    if not rows:
        return [f"{filename}: no data records"]

    for number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            return [f"{filename}: incorrect field count at line {number}"]

    return []


def main():
    failures = []

    for filename, columns in SCHEMAS.items():
        issues = validate_csv(filename, columns)

        if issues:
            failures.extend(issues)
            for issue in issues:
                print(f"FAIL: {issue}")
        else:
            print(f"PASS: {filename}")

    if failures:
        print(f"\nValidation FAILED: {len(failures)} issue(s)")
        return 1

    print("\nValidation PASSED: all CSV structures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
