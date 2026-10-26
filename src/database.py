
import sqlite3
from pathlib import Path
from contextlib import contextmanager

# Find the main project folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "employees.db"


@contextmanager
def database_connection(db_path):
    """Open a connection and always close it."""
    connection = sqlite3.connect(db_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(db_path=DB_PATH):
    """Create the employee table if it does not exist."""
    with database_connection(db_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                city TEXT NOT NULL
            )
        """)


def add_employee(employee_id, first_name, last_name,
                 department, email, city, db_path=DB_PATH):
    """Validate and add a new employee."""
    values = [
        employee_id.strip(), first_name.strip(), last_name.strip(),
        department.strip(), email.strip(), city.strip()
    ]

    if not all(values):
        raise ValueError("All employee fields are required.")

    employee_id, first_name, last_name, department, email, city = values

    try:
        with database_connection(db_path) as connection:
            connection.execute("""
                INSERT INTO employees
                (employee_id, first_name, last_name, department, email, city)
                VALUES (?, ?, ?, ?, ?, ?)
            """, values)
    except sqlite3.IntegrityError as error:
        message = str(error).lower()

        if "employees.employee_id" in message:
            raise ValueError(
                "This employee ID already exists."
            ) from error

        if "employees.email" in message:
            raise ValueError(
                "This email is already registered."
            ) from error

        raise ValueError("Employee could not be saved.") from error


def get_all_employees(db_path=DB_PATH):
    """Return every employee."""
    with database_connection(db_path) as connection:
        cursor = connection.execute("""
            SELECT employee_id, first_name, last_name,
                   department, email, city
            FROM employees
            ORDER BY employee_id
        """)
        return cursor.fetchall()


def get_employee_by_id(employee_id, db_path=DB_PATH):
    """Find one employee using their exact ID."""
    with database_connection(db_path) as connection:
        cursor = connection.execute("""
            SELECT employee_id, first_name, last_name,
                   department, email, city
            FROM employees
            WHERE employee_id = ?
        """, (employee_id.strip(),))
        return cursor.fetchone()


def search_employees(search_text, db_path=DB_PATH):
    """Search across employee fields."""
    pattern = f"%{search_text.strip()}%"

    with database_connection(db_path) as connection:
        cursor = connection.execute("""
            SELECT employee_id, first_name, last_name,
                   department, email, city
            FROM employees
            WHERE employee_id LIKE ?
               OR first_name LIKE ?
               OR last_name LIKE ?
               OR department LIKE ?
               OR email LIKE ?
               OR city LIKE ?
            ORDER BY employee_id
        """, (pattern,) * 6)
        return cursor.fetchall()


def update_employee(employee_id, first_name, last_name,
                    department, email, city, db_path=DB_PATH):
    """Update an existing employee without changing their ID."""
    values = [
        employee_id.strip(), first_name.strip(), last_name.strip(),
        department.strip(), email.strip(), city.strip()
    ]

    if not all(values):
        raise ValueError("All employee fields are required.")

    employee_id, first_name, last_name, department, email, city = values

    try:
        with database_connection(db_path) as connection:
            cursor = connection.execute("""
                UPDATE employees
                SET first_name = ?, last_name = ?,
                    department = ?, email = ?, city = ?
                WHERE employee_id = ?
            """, (
                first_name, last_name, department,
                email, city, employee_id
            ))

            if cursor.rowcount == 0:
                raise ValueError("Employee ID was not found.")

    except sqlite3.IntegrityError as error:
        raise ValueError(
            "This email is already registered to another employee."
        ) from error


def delete_employee(employee_id, db_path=DB_PATH):
    """Delete an employee by ID."""
    with database_connection(db_path) as connection:
        cursor = connection.execute("""
            DELETE FROM employees WHERE employee_id = ?
        """, (employee_id.strip(),))

        if cursor.rowcount == 0:
            raise ValueError("Employee ID was not found.")


# Create the database when this module is run directly.
if __name__ == "__main__":
    initialize_database()
    print("Employee database is ready.")