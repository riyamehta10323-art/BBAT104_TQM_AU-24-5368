"""
Web Application Route & Functionality Tests
BBAT104: Total Quality Management (Q06: Reduce Duplicate Entries)
Tests Flask routes, Poka-Yoke validation, and database integration in isolation.
"""

import tempfile
import unittest
from pathlib import Path

from app import app
from src.database import (
    initialize_database,
    add_employee,
    get_all_employees,
    get_employee_by_id,
)


class EmployeeWebAppTests(unittest.TestCase):

    def setUp(self):
        """Set up an isolated temporary database for each web test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_web.db"
        initialize_database(self.db_path)

        app.config["TESTING"] = True
        app.config["DB_PATH"] = self.db_path
        app.config["SECRET_KEY"] = "test-secret-key"
        self.client = app.test_client()

    def tearDown(self):
        """Clean up temporary test artifacts."""
        self.temp_dir.cleanup()

    def add_sample_record(self, emp_id="E001", email="riya@example.com"):
        """Helper to insert a clean sample record."""
        add_employee(
            emp_id, "Riya", "Mehta", "Engineering", email, "Haldwani",
            db_path=self.db_path
        )

    def test_dashboard_loads_successfully(self):
        """Test GET / renders dashboard with 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Employee Management System", response.data)
        self.assertIn(b"Total Employees", response.data)

    def test_add_page_loads_successfully(self):
        """Test GET /add renders the form."""
        response = self.client.get("/add")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add New Employee", response.data)
        self.assertIn(b"TQM Q06 Integrity Rules", response.data)

    def test_add_employee_success(self):
        """Test POST /add successfully saves a valid employee and redirects."""
        payload = {
            "employee_id": "E100",
            "first_name": "John",
            "last_name": "Doe",
            "department": "IT",
            "email": "john.doe@example.com",
            "city": "Bengaluru",
        }
        response = self.client.post("/add", data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"added successfully", response.data)

        # Verify directly in SQLite
        saved = get_employee_by_id("E100", db_path=self.db_path)
        self.assertIsNotNone(saved)
        self.assertEqual(saved[1], "John")

    def test_add_employee_missing_fields_rejected(self):
        """Test POST /add with blank values returns 400."""
        payload = {
            "employee_id": "E101",
            "first_name": "",
            "last_name": "Doe",
            "department": "IT",
            "email": "john@example.com",
            "city": "Delhi",
        }
        response = self.client.post("/add", data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"All employee fields are required", response.data)

    def test_add_employee_invalid_email_regex_rejected(self):
        """Test POST /add with invalid email syntax returns 400."""
        payload = {
            "employee_id": "E102",
            "first_name": "Jane",
            "last_name": "Doe",
            "department": "HR",
            "email": "invalid-email-address",
            "city": "Mumbai",
        }
        response = self.client.post("/add", data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please enter a valid email address", response.data)

    def test_add_duplicate_employee_id_case_insensitive_rejected(self):
        """Quality Goal Q06: Reject duplicate ID regardless of casing."""
        self.add_sample_record("E001", "first@example.com")

        # Attempt to insert lowercase 'e001'
        payload = {
            "employee_id": "e001",
            "first_name": "Different",
            "last_name": "Person",
            "department": "Finance",
            "email": "second@example.com",
            "city": "Chennai",
        }
        response = self.client.post("/add", data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"already exists", response.data)

    def test_add_duplicate_email_case_insensitive_rejected(self):
        """Quality Goal Q06: Reject duplicate email regardless of casing."""
        self.add_sample_record("E001", "riya@example.com")

        # Attempt to insert uppercase email 'RIYA@EXAMPLE.COM' under new ID
        payload = {
            "employee_id": "E002",
            "first_name": "New",
            "last_name": "Person",
            "department": "Finance",
            "email": "RIYA@EXAMPLE.COM",
            "city": "Chennai",
        }
        response = self.client.post("/add", data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"already registered", response.data)

    def test_search_employees_route(self):
        """Test search query filters matching employees on dashboard."""
        self.add_sample_record("E001", "riya@example.com")
        add_employee(
            "E002", "Amit", "Sharma", "Finance", "amit@example.com", "Pune",
            db_path=self.db_path
        )

        response = self.client.get("/?search=Amit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Amit", response.data)
        self.assertNotIn(b"Haldwani", response.data)

    def test_edit_page_loads_with_locked_id(self):
        """Test GET /edit/<id> renders form with readonly ID field."""
        self.add_sample_record("E001", "riya@example.com")

        response = self.client.get("/edit/E001")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Edit Employee Details", response.data)
        self.assertIn(b"readonly", response.data)
        self.assertIn(b"Form Key Locking", response.data)

    def test_edit_employee_post_updates_record(self):
        """Test POST /edit/<id> modifies fields."""
        self.add_sample_record("E001", "riya@example.com")

        payload = {
            "first_name": "Riya",
            "last_name": "Mehta",
            "department": "Quality Assurance",
            "email": "riya@example.com",
            "city": "Nainital",
        }
        response = self.client.post(
            "/edit/E001", data=payload, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"updated successfully", response.data)

        updated = get_employee_by_id("E001", db_path=self.db_path)
        self.assertEqual(updated[3], "Quality Assurance")
        self.assertEqual(updated[5], "Nainital")

    def test_edit_employee_duplicate_email_rejected(self):
        """Test editing an employee's email to another employee's email is rejected."""
        self.add_sample_record("E001", "first@example.com")
        add_employee(
            "E002", "Bob", "Jones", "IT", "second@example.com", "Goa",
            db_path=self.db_path
        )

        payload = {
            "first_name": "Bob",
            "last_name": "Jones",
            "department": "IT",
            "email": "FIRST@EXAMPLE.COM",  # Collision with E001
            "city": "Goa",
        }
        response = self.client.post("/edit/E002", data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"already registered to another employee", response.data)

    def test_delete_employee_success(self):
        """Test POST /delete/<id> deletes the record from database."""
        self.add_sample_record("E001", "riya@example.com")

        response = self.client.post("/delete/E001", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"deleted successfully", response.data)
        self.assertIsNone(get_employee_by_id("E001", db_path=self.db_path))

    def test_edit_employee_missing_fields_rejected(self):
        """Test POST /edit/<id> with missing fields returns 400 and preserves original record."""
        self.add_sample_record("E001", "riya@example.com")

        payload = {
            "first_name": "",  # Missing required field
            "last_name": "Mehta",
            "department": "Engineering",
            "email": "riya@example.com",
            "city": "Haldwani",
        }
        response = self.client.post("/edit/E001", data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"All employee fields are required", response.data)

        # Confirm database record was not corrupted
        original = get_employee_by_id("E001", db_path=self.db_path)
        self.assertEqual(original[1], "Riya")

    def test_edit_employee_invalid_email_regex_rejected(self):
        """Test POST /edit/<id> with invalid email format returns 400 and preserves original record."""
        self.add_sample_record("E001", "riya@example.com")

        payload = {
            "first_name": "Riya",
            "last_name": "Mehta",
            "department": "Engineering",
            "email": "invalid-email-format",
            "city": "Haldwani",
        }
        response = self.client.post("/edit/E001", data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please enter a valid email address", response.data)

        # Confirm database record was not corrupted
        original = get_employee_by_id("E001", db_path=self.db_path)
        self.assertEqual(original[4], "riya@example.com")


if __name__ == "__main__":
    unittest.main()
