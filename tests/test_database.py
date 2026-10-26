
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.database import (
    initialize_database,
    add_employee,
    get_all_employees,
    get_employee_by_id,
    search_employees,
    update_employee,
    delete_employee,
)


class EmployeeDatabaseTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(
            Path(self.temp_dir.name) / "test_employees.db"
        )
        initialize_database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def add_sample_employee(self):
        add_employee(
            "E001", "Riya", "Mehta",
            "CSE", "riya@example.com", "Haldwani",
            db_path=self.db_path
        )

    def test_add_and_read_employee(self):
        self.add_sample_employee()
        employees = get_all_employees(self.db_path)

        self.assertEqual(len(employees), 1)
        self.assertEqual(employees[0][0], "E001")

    def test_duplicate_employee_id_is_rejected(self):
        self.add_sample_employee()

        with self.assertRaisesRegex(ValueError, "ID already exists"):
            add_employee(
                "E001", "Another", "Person",
                "IT", "another@example.com", "Delhi",
                db_path=self.db_path
            )

    def test_duplicate_email_is_rejected(self):
        self.add_sample_employee()

        with self.assertRaisesRegex(ValueError, "email is already"):
            add_employee(
                "E002", "Another", "Person",
                "IT", "riya@example.com", "Delhi",
                db_path=self.db_path
            )

    def test_empty_fields_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "required"):
            add_employee(
                "E003", "  ", "Person",
                "IT", "person@example.com", "Delhi",
                db_path=self.db_path
            )

    def test_search_employee(self):
        self.add_sample_employee()
        results = search_employees("Riya", self.db_path)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "E001")

    def test_update_employee(self):
        self.add_sample_employee()

        update_employee(
            "E001", "Riya", "Mehta",
            "Engineering", "riya@example.com", "Haldwani",
            db_path=self.db_path
        )

        employees = get_all_employees(self.db_path)
        self.assertEqual(employees[0][3], "Engineering")

    def test_delete_employee(self):
        self.add_sample_employee()

        delete_employee("E001", self.db_path)

        self.assertEqual(get_all_employees(self.db_path), [])

    def test_duplicate_employee_id_case_insensitive_is_rejected(self):
        self.add_sample_employee()

        with self.assertRaisesRegex(ValueError, "ID already exists"):
            add_employee(
                "e001", "Another", "Person",
                "IT", "another@example.com", "Delhi",
                db_path=self.db_path
            )

    def test_duplicate_email_case_insensitive_is_rejected(self):
        self.add_sample_employee()

        with self.assertRaisesRegex(ValueError, "email is already"):
            add_employee(
                "E002", "Another", "Person",
                "IT", "Riya@Example.Com", "Delhi",
                db_path=self.db_path
            )

    def test_get_employee_by_id_case_insensitive(self):
        self.add_sample_employee()

        record_upper = get_employee_by_id("E001", self.db_path)
        record_lower = get_employee_by_id("e001", self.db_path)

        self.assertIsNotNone(record_upper)
        self.assertIsNotNone(record_lower)
        self.assertEqual(record_upper[0], "E001")
        self.assertEqual(record_lower[0], "E001")

    def test_update_employee_rejects_duplicate_email_case_insensitive(self):
        self.add_sample_employee()
        add_employee(
            "E002", "Aarav", "Sharma",
            "IT", "aarav@example.com", "Delhi",
            db_path=self.db_path
        )

        with self.assertRaisesRegex(ValueError, "already registered"):
            update_employee(
                "E002", "Aarav", "Sharma",
                "IT", "RIYA@EXAMPLE.COM", "Delhi",
                db_path=self.db_path
            )

    def test_update_employee_allows_retaining_own_email(self):
        self.add_sample_employee()

        update_employee(
            "E001", "Riya", "Mehta",
            "Engineering", "riya@example.com", "Dehradun",
            db_path=self.db_path
        )

        employee = get_employee_by_id("E001", self.db_path)
        self.assertEqual(employee[3], "Engineering")
        self.assertEqual(employee[4], "riya@example.com")
        self.assertEqual(employee[5], "Dehradun")

    def test_update_employee_allows_casing_change_on_own_email(self):
        self.add_sample_employee()

        update_employee(
            "E001", "Riya", "Mehta",
            "CSE", "Riya@Example.com", "Haldwani",
            db_path=self.db_path
        )

        employee = get_employee_by_id("E001", self.db_path)
        self.assertEqual(employee[4], "Riya@Example.com")

    def test_delete_employee_case_insensitive(self):
        self.add_sample_employee()

        delete_employee("e001", self.db_path)

        self.assertEqual(get_all_employees(self.db_path), [])

    def test_legacy_database_backward_compatibility(self):
        legacy_db_path = str(Path(self.temp_dir.name) / "legacy_employees.db")
        # Simulate an existing database created with the old schema (without COLLATE NOCASE)
        conn = sqlite3.connect(legacy_db_path)
        with conn:
            conn.execute("""
                CREATE TABLE employees (
                    employee_id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    city TEXT NOT NULL
                )
            """)
            conn.execute(
                "INSERT INTO employees VALUES ('E999', 'Old', 'Record', 'Admin', 'old@example.com', 'Pune')"
            )
        conn.close()

        # Run initialize_database on legacy database
        initialize_database(legacy_db_path)

        # Verify that existing records are preserved
        existing = get_employee_by_id("e999", legacy_db_path)
        self.assertIsNotNone(existing)
        self.assertEqual(existing[0], "E999")

        # Verify case-insensitive duplicate ID is rejected on legacy DB
        with self.assertRaisesRegex(ValueError, "ID already exists"):
            add_employee(
                "e999", "New", "Person",
                "HR", "new@example.com", "Mumbai",
                db_path=legacy_db_path
            )

        # Verify case-insensitive duplicate Email is rejected on legacy DB
        with self.assertRaisesRegex(ValueError, "email is already"):
            add_employee(
                "E998", "New", "Person",
                "HR", "Old@EXAMPLE.com", "Mumbai",
                db_path=legacy_db_path
            )


if __name__ == "__main__":
    unittest.main()
