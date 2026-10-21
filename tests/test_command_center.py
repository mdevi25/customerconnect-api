
"""Regression tests for the AIDLC Command Center validator."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import validate_command_center as validator


class CommandCenterTests(unittest.TestCase):

    def setUp(self):
        self.original_read_csv = validator.read_csv

    def altered_rows(self, filename, change):
        """Test modified records without changing actual CSV files."""
        original = self.original_read_csv

        def fake_read_csv(requested):
            columns, rows = original(requested)
            if requested == filename:
                rows = [row.copy() for row in rows]
                change(rows)
            return columns, rows

        return patch.object(validator, "read_csv", fake_read_csv)

    def test_01_all_csv_structures(self):
        for filename, schema in validator.SCHEMAS.items():
            with self.subTest(filename=filename):
                self.assertEqual(
                    validator.validate_csv(filename, schema), []
                )

    def test_02_valid_dependencies(self):
        self.assertEqual(validator.validate_dependencies(), [])

    def test_03_unknown_dependency(self):
        with self.altered_rows(
            "execution_plan.csv",
            lambda rows: rows[0].update(dependency="UNKNOWN-999")
        ):
            issues = validator.validate_dependencies()
            self.assertTrue(any("unknown work_id UNKNOWN-999" in x
                                for x in issues))

    def test_04_circular_dependency(self):
        with self.altered_rows(
            "execution_plan.csv",
            lambda rows: rows[0].update(dependency="M1-02")
        ):
            issues = validator.validate_dependencies()
            self.assertIn(
                "Dependency cycle: M1-01 -> M1-02 -> M1-01",
                issues
            )

    def test_05_self_dependency(self):
        with self.altered_rows(
            "execution_plan.csv",
            lambda rows: rows[0].update(dependency="M1-01")
        ):
            issues = validator.validate_dependencies()
            self.assertIn(
                "Dependency: M1-01 depends on itself", issues
            )

    def test_06_duplicate_work_id(self):
        with self.altered_rows(
            "execution_plan.csv",
            lambda rows: rows[1].update(work_id="M1-01")
        ):
            issues = validator.validate_dependencies()
            self.assertIn(
                "Dependency: duplicate work_id M1-01", issues
            )

    def test_07_valid_approvals(self):
        self.assertEqual(validator.validate_approvals(), [])

    def test_08_duplicate_approval(self):
        with self.altered_rows(
            "approval_register.csv",
            lambda rows: rows[1].update(
                approval_id=rows[0]["approval_id"]
            )
        ):
            issues = validator.validate_approvals()
            self.assertTrue(any("duplicate approval_id" in x
                                for x in issues))

    def test_09_missing_approval_field(self):
        with self.altered_rows(
            "approval_register.csv",
            lambda rows: rows[0].update(approver_role="")
        ):
            issues = validator.validate_approvals()
            self.assertTrue(any("missing approver_role" in x
                                for x in issues))

    def test_10_invalid_status(self):
        with self.altered_rows(
            "approval_register.csv",
            lambda rows: rows[0].update(decision_status="INVALID")
        ):
            issues = validator.validate_approvals()
            self.assertTrue(any("invalid status" in x for x in issues))

    def test_11_invalid_date(self):
        with self.altered_rows(
            "approval_register.csv",
            lambda rows: rows[0].update(decision_date="2026-99-99")
        ):
            issues = validator.validate_approvals()
            self.assertTrue(any("invalid decision_date" in x
                                for x in issues))

    def test_12_missing_artifact(self):
        with self.altered_rows(
            "approval_register.csv",
            lambda rows: rows[0].update(
                artifact_path="missing/file.md"
            )
        ):
            issues = validator.validate_approvals()
            self.assertTrue(any("artifact not found" in x
                                for x in issues))

    def test_13_unsafe_artifact_path(self):
        with self.altered_rows(
            "approval_register.csv",
            lambda rows: rows[0].update(
                artifact_path="../../outside.md"
            )
        ):
            issues = validator.validate_approvals()
            self.assertTrue(any("artifact outside repository" in x
                                for x in issues))


if __name__ == "__main__":
    unittest.main()
