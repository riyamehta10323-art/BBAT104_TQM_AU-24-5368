
import tempfile
import unittest
from pathlib import Path

from src.database import (
    initialize_database,
    add_employee,
    get_all_employees,
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


if __name__ == "__main__":
    unittest.main()