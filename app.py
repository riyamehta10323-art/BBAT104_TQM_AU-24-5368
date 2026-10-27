"""
Employee Management System - Flask Web Application
BBAT104: Total Quality Management
Quality Goal Q06: Reduce Duplicate Entries
Author: Riya Mehta (AU-24-5368)
"""

import os
import re
from pathlib import Path
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from src.database import (
    initialize_database,
    add_employee,
    get_all_employees,
    get_employee_by_id,
    search_employees,
    update_employee,
    delete_employee,
    DB_PATH,
)

# Email regex matching the original Tkinter validation in src/main.py
EMAIL_REGEX = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bbat104-tqm-q06-secret-key-2026")
app.config["DB_PATH"] = DB_PATH


def get_active_db_path():
    """Return the currently configured SQLite database path."""
    return app.config.get("DB_PATH", DB_PATH)


@app.route("/", methods=["GET"])
def index():
    """Main dashboard displaying employees, search bar, and KPI metrics."""
    db_path = get_active_db_path()
    search_query = request.args.get("search", "").strip()

    if search_query:
        employees = search_employees(search_query, db_path=db_path)
    else:
        employees = get_all_employees(db_path=db_path)

    # Calculate overall metrics from complete database
    all_records = get_all_employees(db_path=db_path)
    total_employees = len(all_records)
    departments = sorted(list(set(emp[3] for emp in all_records if emp[3])))

    return render_template(
        "index.html",
        employees=employees,
        search_query=search_query,
        total_employees=total_employees,
        total_departments=len(departments),
        departments=departments,
    )


@app.route("/add", methods=["GET", "POST"])
def add_employee_route():
    """Add a new employee with client and server-side duplicate prevention."""
    db_path = get_active_db_path()

    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        city = request.form.get("city", "").strip()

        # Tier 1 Validation: All fields mandatory
        if not all([employee_id, first_name, last_name, department, email, city]):
            flash("All employee fields are required.", "danger")
            return render_template("add_employee.html", form_data=request.form), 400

        # Tier 1 Validation: Email syntax regex
        if not EMAIL_REGEX.fullmatch(email):
            flash("Please enter a valid email address.", "danger")
            return render_template("add_employee.html", form_data=request.form), 400

        # Tier 2 Poka-Yoke: Pre-add exact and case-insensitive ID check
        if get_employee_by_id(employee_id, db_path=db_path) is not None:
            flash(
                f"Employee ID '{employee_id}' already exists (case-insensitive check).",
                "danger",
            )
            return render_template("add_employee.html", form_data=request.form), 400

        # Tier 3 Database Insertion (enforces UNIQUE COLLATE NOCASE)
        try:
            add_employee(
                employee_id,
                first_name,
                last_name,
                department,
                email,
                city,
                db_path=db_path,
            )
            flash(
                f"Employee {first_name} {last_name} ({employee_id}) added successfully.",
                "success",
            )
            return redirect(url_for("index"))

        except ValueError as error:
            flash(str(error), "danger")
            return render_template("add_employee.html", form_data=request.form), 400

        except Exception as error:
            flash(f"Unexpected database error: {error}", "danger")
            return render_template("add_employee.html", form_data=request.form), 500

    return render_template("add_employee.html", form_data={})


@app.route("/edit/<employee_id>", methods=["GET", "POST"])
def edit_employee_route(employee_id):
    """Edit existing employee. The Employee ID is locked and immutable."""
    db_path = get_active_db_path()
    existing = get_employee_by_id(employee_id, db_path=db_path)

    if not existing:
        flash(f"Employee ID '{employee_id}' was not found.", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        city = request.form.get("city", "").strip()

        # Validation: Mandatory fields
        if not all([first_name, last_name, department, email, city]):
            flash("All employee fields are required.", "danger")
            employee_data = (employee_id, first_name, last_name, department, email, city)
            return render_template("edit_employee.html", employee=employee_data), 400

        # Validation: Email regex
        if not EMAIL_REGEX.fullmatch(email):
            flash("Please enter a valid email address.", "danger")
            employee_data = (employee_id, first_name, last_name, department, email, city)
            return render_template("edit_employee.html", employee=employee_data), 400

        # Database Update: The ID from the URL is strictly used (prevents primary key alteration)
        try:
            update_employee(
                employee_id,
                first_name,
                last_name,
                department,
                email,
                city,
                db_path=db_path,
            )
            flash(
                f"Employee {employee_id} updated successfully.",
                "success",
            )
            return redirect(url_for("index"))

        except ValueError as error:
            flash(str(error), "danger")
            employee_data = (employee_id, first_name, last_name, department, email, city)
            return render_template("edit_employee.html", employee=employee_data), 400

        except Exception as error:
            flash(f"Unexpected update error: {error}", "danger")
            employee_data = (employee_id, first_name, last_name, department, email, city)
            return render_template("edit_employee.html", employee=employee_data), 500

    return render_template("edit_employee.html", employee=existing)


@app.route("/delete/<employee_id>", methods=["POST"])
def delete_employee_route(employee_id):
    """Delete an employee after user confirmation."""
    db_path = get_active_db_path()

    try:
        delete_employee(employee_id, db_path=db_path)
        flash(f"Employee '{employee_id}' was deleted successfully.", "success")
    except ValueError as error:
        flash(str(error), "danger")
    except Exception as error:
        flash(f"Error deleting employee: {error}", "danger")

    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(e):
    flash("The requested page was not found.", "warning")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Ensure database tables and indexes exist on the default database
    initialize_database(get_active_db_path())
    print("=" * 65)
    print(" Employee Management System - Flask Web Application")
    print(" Course: BBAT104 Total Quality Management")
    print(" Quality Goal: Q06 - Reduce Duplicate Entries")
    print(f" Database: {get_active_db_path()}")
    print(" Local URL: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(debug=True, host="127.0.0.1", port=5000)
