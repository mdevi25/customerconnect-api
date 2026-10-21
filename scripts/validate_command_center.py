
"""Validate AIDLC Command Center CSV structures and dependencies."""

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


def read_csv(filename):
    path = ROOT / filename
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def validate_csv(filename, expected_columns):
    path = ROOT / filename

    if not path.is_file():
        return [f"{filename}: file missing"]

    try:
        columns, rows = read_csv(filename)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [f"{filename}: cannot read CSV: {exc}"]

    issues = []

    if columns != expected_columns:
        issues.append(f"{filename}: incorrect columns or column order")

    if not rows:
        issues.append(f"{filename}: no data records")

    for number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            issues.append(
                f"{filename}: incorrect field count at line {number}"
            )

    return issues


def validate_dependencies():
    """Check IDs, dependency references and circular relationships."""
    _, rows = read_csv("execution_plan.csv")
    issues = []
    graph = {}

    # Build dependency graph.
    for row in rows:
        work_id = row["work_id"].strip()
        raw_dependency = row["dependency"].strip()

        if not work_id:
            issues.append("Dependency: empty work_id")
            continue

        if work_id in graph:
            issues.append(f"Dependency: duplicate work_id {work_id}")
            continue

        if raw_dependency == "NONE":
            dependencies = []
        else:
            dependencies = [
                item.strip()
                for item in raw_dependency.split(";")
            ]

            if not raw_dependency or any(not item for item in dependencies):
                issues.append(
                    f"Dependency: {work_id} has an empty prerequisite"
                )

        graph[work_id] = dependencies

    # Check that every prerequisite exists.
    for work_id, dependencies in graph.items():
        for dependency in dependencies:
            if dependency not in graph:
                issues.append(
                    f"Dependency: {work_id} references "
                    f"unknown work_id {dependency}"
                )

            if dependency == work_id:
                issues.append(
                    f"Dependency: {work_id} depends on itself"
                )

    # Detect cycles using depth-first search.
    visited = set()
    active = set()
    reported_cycles = set()

    def visit(work_id, path):
        if work_id in active:
            start = path.index(work_id)
            cycle = path[start:]
            cycle_text = " -> ".join(cycle)

            if cycle_text not in reported_cycles:
                issues.append(f"Dependency cycle: {cycle_text}")
                reported_cycles.add(cycle_text)
            return

        if work_id in visited:
            return

        active.add(work_id)

        for dependency in graph[work_id]:
            if dependency in graph:
                visit(dependency, path + [dependency])

        active.remove(work_id)
        visited.add(work_id)

    for work_id in graph:
        visit(work_id, [work_id])

    return issues



def validate_approvals():
    """Validate approval records without authenticating decisions."""
    _, rows = read_csv("approval_register.csv")
    issues = []
    seen = set()
    required = SCHEMAS["approval_register.csv"]
    allowed = {"APPROVED", "REJECTED", "PENDING", "NEEDS_REVISION"}
    repo = ROOT.parent.resolve()

    from datetime import date

    for number, row in enumerate(rows, 2):
        approval_id = (row.get("approval_id") or "").strip()
        label = approval_id or f"line {number}"

        for field in required:
            if not (row.get(field) or "").strip():
                issues.append(f"Approval {label}: missing {field}")

        if not approval_id:
            continue

        if approval_id in seen:
            issues.append(f"Approval: duplicate approval_id {approval_id}")
        seen.add(approval_id)

        status = (row.get("decision_status") or "").strip()
        if status and status not in allowed:
            issues.append(f"Approval {approval_id}: invalid status {status}")

        value = (row.get("decision_date") or "").strip()
        if value:
            try:
                parsed = date.fromisoformat(value)
                if parsed.isoformat() != value:
                    raise ValueError()
            except ValueError:
                issues.append(f"Approval {approval_id}: invalid decision_date {value}")

        artifact_path = (row.get("artifact_path") or "").strip()
        if artifact_path:
            artifact = (repo / artifact_path).resolve()
            if not artifact.is_relative_to(repo):
                issues.append(f"Approval {approval_id}: artifact outside repository")
            elif not artifact.is_file():
                issues.append(f"Approval {approval_id}: artifact not found {artifact_path}")

    return issues


def main():
    failures = []
    csv_results = {}

    # Task 1: CSV structure validation.
    for filename, columns in SCHEMAS.items():
        issues = validate_csv(filename, columns)
        csv_results[filename] = issues

        if issues:
            failures.extend(issues)
            for issue in issues:
                print(f"FAIL: {issue}")
        else:
            print(f"PASS: {filename}")

    # Task 2: Run dependency checks only if the CSV is valid.
    if not csv_results["execution_plan.csv"]:
        dependency_issues = validate_dependencies()

        if dependency_issues:
            failures.extend(dependency_issues)
            for issue in dependency_issues:
                print(f"FAIL: {issue}")
        else:
            print("PASS: dependency references and cycle checks")
    else:
        print("SKIP: dependency checks (execution plan CSV invalid)")

    # Task 3: Approval-record validation.
    if not csv_results["approval_register.csv"]:
        approval_issues = validate_approvals()
        if approval_issues:
            failures.extend(approval_issues)
            for issue in approval_issues:
                print(f"FAIL: {issue}")
        else:
            print("PASS: approval record checks")
    else:
        print("SKIP: approval checks (approval register CSV invalid)")

    if failures:
        print(f"\nValidation FAILED: {len(failures)} issue(s)")
        return 1

    print("\nValidation PASSED: all implemented checks are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())