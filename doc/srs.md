# Software Requirements Specification (SRS)
## Employee Management System — Q06: Reduce Duplicate Entries

- **Course:** BBAT104 — Total Quality Management (TQM)
- **Quality Objective:** Q06 — Reduce Duplicate Entries
- **Author / Student ID:** Riya Mehta (AU-24-5368)
- **Document Version:** 2.0 (Dual-Interface Desktop & Web Specification)
- **Document Path:** `doc/srs.md`
- **Related Documents:** `doc/system-architecture.md`, `doc/defect-and-root-cause.md`, `doc/test-report.md`, `README.md`

---

## 1. Introduction and Purpose

### 1.1 Purpose
This Software Requirements Specification (SRS) document details the functional, non-functional, and quality requirements for the **Employee Management System (EMS)**. It serves as the baseline for Review 1 (Setup & SRS) and Review 2 (Base System & CRUD) in the BBAT104 Total Quality Management course curriculum.

### 1.2 Document Conventions
* **FR-xx**: Functional Requirement identifier.
* **NFR-xx**: Non-Functional Requirement identifier.
* Requirements marked **[Implemented]** reflect verified behaviors in the current codebase (`src/database.py`, `src/main.py`, `app.py`).
* Requirements marked **[Planned Improvement]** indicate recognized enhancement opportunities identified during quality audits for future phases.

### 1.3 Intended Audience
* Course faculty and external evaluators assessing Review 1 and Review 2 criteria.
* The student developer responsible for implementation, testing, and maintenance.

---

## 2. Project Objectives & TQM Context

### 2.1 Project Goal
The primary objective of the Employee Management System is to provide a reliable, dual-interface record management solution (Desktop GUI and Modern Web Application) that maintains organized personnel data while preventing dirty, inaccurate, or redundant employee entries.

### 2.2 TQM Quality Goal Q06: Reduce Duplicate Entries
In Total Quality Management (TQM) and data quality engineering, duplicate records are categorized as **input-stage defects**. Unchecked duplicate entries introduce significant organizational friction:
* Inaccurate headcount calculations and flawed personnel metrics.
* Payroll errors and split performance records.
* Communication breakdowns resulting from redundant or divergent contact addresses.
* Excessive human overhead spent manually auditing and reconciling conflicting entries.

### 2.3 Poka-Yoke (Mistake-Proofing) Principle
Under traditional data management, duplicate entries are cleaned up through periodic post-hoc audits (defect detection). Under TQM, the system implements **Poka-Yoke (defect prevention at the source)**. The application is structured so that accidental duplicate entries—whether due to exact re-entry, casing variations, or premature confirmation—are intercepted and prevented before they can be committed to persistent storage.

---

## 3. System Architecture & Technology Stack

### 3.1 Dual-Interface Shared Engine Architecture
The system provides two distinct user interfaces operating against a single shared backend data layer:
1. **Desktop Presentation (`src/main.py`):** Built with Python's standard `tkinter` and `ttk` library. Provides a native desktop application with form inputs, action buttons, search bar, scrollable Treeview table, and modal confirmation dialogs.
2. **Web Presentation (`app.py`):** Built with `Flask`, Jinja2 HTML templates, and `Bootstrap 5`. Provides a modern, responsive web dashboard accessible via standard web browsers at `http://127.0.0.1:5000`.
3. **Shared Backend Data Access (`src/database.py`):** Uses Python's standard `sqlite3` library to execute relational storage operations, manage database connections, and enforce case-insensitive uniqueness constraints across both interfaces.
4. **Relational Storage (`employees.db`):** A shared, single SQLite relational database file located at the repository root.

### 3.2 Technology Stack
* **Programming Language:** Python 3 (verified on Python 3.14.6 64-bit)
* **Desktop GUI Toolkit:** Tkinter / TTK (standard library)
* **Web Framework:** Flask (v3.1.3+)
* **Templating & UI:** Jinja2, HTML5, Custom CSS (`static/css/style.css`), Bootstrap 5.3.3 (via CDN), Bootstrap Icons 1.11.3
* **Database Engine:** SQLite 3 (verified on SQLite 3.50.4 with B-Tree indexes)
* **Test Runner:** Python standard library `unittest` (29 automated unit and integration tests)
* **Development & Version Control:** Visual Studio Code, Git, GitHub

### 3.3 System Constraints
* **Workstation Deployment:** The software executes locally as a single-station application (desktop or local web server on `127.0.0.1:5000`); it is not currently deployed as an enterprise multi-tenant cloud application.
* **Shared Local Storage:** All records persist in a single local database file (`employees.db`) in the project directory, accessed concurrently by either interface.

---

## 4. User Characteristics and User Interactions

### 4.1 Intended Users
The intended primary user is a human resources assistant, administrative clerk, or departmental operator responsible for maintaining employee records within an organization. Users operate either via the desktop window or through their preferred web browser.

### 4.2 Standard User Workflows
1. **Adding an Employee:** User fills form fields, initiates the action, responds to the confirmation prompt (Tkinter `messagebox.askyesno` or Bootstrap modal), and views the updated record in the table upon success.
2. **Searching Employees:** User enters a search query in the search bar, clicks "Search", and views filtered records matching any employee attribute. Clicking "Show All" or "Clear" resets the view.
3. **Updating an Employee:** User selects an existing employee row (which locks the Employee ID and populates fields), modifies editable fields, initiates the update, confirms the action, and saves changes.
4. **Deleting an Employee:** User selects an employee, clicks "Delete", and confirms the destructive deletion dialog.
5. **Form Clearing:** User clicks "Clear Form" or navigates back to reset entries and restore the Employee ID field to an editable state.

---

## 5. Scope and Boundaries

### 5.1 In-Scope Items
* **Core CRUD Functionality:** Creating, retrieving, searching, updating, and deleting employee records with standard attributes:
  - `employee_id` (Text identifier, e.g., "E001")
  - `first_name` (Text string)
  - `last_name` (Text string)
  - `department` (Text string)
  - `email` (Text string)
  - `city` (Text string)
* **Defect Prevention Mechanisms (Q06):**
  - Database primary key constraint on `employee_id`.
  - Database unique constraint on `email`.
  - Case-insensitive uniqueness enforcement (`COLLATE NOCASE` and unique B-tree indexes).
  - Pre-add duplicate ID check in the user interface before confirmation.
  - Form field locking (ID field disabled in Tkinter; `readonly` attribute in Flask) during update operations to prevent duplicate key creation.
  - User confirmation dialogs (`askyesno` in desktop; Bootstrap modal in web) for add, update, and delete actions.
  - Mandatory non-empty validation for all six fields.
  - Email syntax format validation using standard regular expressions (`r"[^@\s]+@[^@\s]+\.[^@\s]+"`).
* **Dual-Interface Availability:** Native Tkinter GUI and responsive Bootstrap 5 Flask web interface.
* **Local SQLite Relational Storage:** Automated database and index creation (`initialize_database`).
* **Automated Regression Suite:** 29 automated tests (15 backend database tests + 14 web route tests) using isolated temporary databases.

### 5.2 Out-of-Scope Items
* Multi-tenant cloud hosting and distributed microservices.
* User authentication, role-based access control (RBAC), and session management.
* Biometric authentication or automated employee identity card scanning.
* Automated phonetic or machine-learning-based demographic fuzzy matching (e.g. soundex matching for human names).
* **CSRF Token Protection:** Form submissions currently use standard HTML forms and POST requests without CSRF token generation (no `Flask-WTF` dependency). This is documented as an academic boundary; public Internet deployments require CSRF tokens.

---

## 6. Functional Requirements

### 6.1 Base CRUD Operations

* **FR-01: Add Employee Record [Implemented]**
  - *Description:* The system shall allow the operator to create a new employee record by providing Employee ID, First Name, Last Name, Department, Email, and City.
  - *Inputs:* Six text strings via GUI form entries or Web form inputs.
  - *Processing:* Inputs are trimmed of whitespace. The system validates that all fields are non-empty, checks email syntax, verifies that the ID does not already exist, prompts for user confirmation, and commits the row to SQLite.
  - *Outputs:* Record inserted into database; table refreshed; form cleared; success confirmation displayed.
  - *Code Reference:* `src/main.py:add_record()`, `app.py:add_employee_route()`, `src/database.py:add_employee()`.

* **FR-02: View All Employees [Implemented]**
  - *Description:* The system shall display all stored employee records in a structured tabular format sorted alphabetically by Employee ID.
  - *Processing:* Queries SQLite using `SELECT ... ORDER BY employee_id COLLATE NOCASE`.
  - *Outputs:* Populated Treeview table (Tkinter) or Bootstrap responsive table (Web).
  - *Code Reference:* `src/main.py:refresh_table()`, `app.py:index()`, `src/database.py:get_all_employees()`.

* **FR-03: Search Employees [Implemented]**
  - *Description:* The system shall filter displayed records matching a user-provided substring across Employee ID, First Name, Last Name, Department, Email, or City.
  - *Inputs:* Search query string.
  - *Processing:* Queries SQLite using parameterized SQL `LIKE ?` pattern matching across all six columns.
  - *Outputs:* Filtered tabular view; status indicator showing matching count.
  - *Code Reference:* `src/main.py:search_records()`, `app.py:index()`, `src/database.py:search_employees()`.

* **FR-04: Select Employee for Modification [Implemented]**
  - *Description:* Selecting an employee record from the table shall populate the form entries with that employee's current data.
  - *Processing:* Extracts row attributes from table selection; populates fields.
  - *Outputs:* Pre-filled form entries; active record indicator.
  - *Code Reference:* `src/main.py:select_record()`, `app.py:edit_employee_route()`.

* **FR-05: Update Employee Record [Implemented]**
  - *Description:* The system shall allow modifying First Name, Last Name, Department, Email, and City for an existing employee.
  - *Processing:* Validates non-empty fields and email format; executes parameterized SQL `UPDATE ... WHERE employee_id = ? COLLATE NOCASE`.
  - *Outputs:* Updated row persisted in SQLite; table refreshed; success confirmation displayed.
  - *Code Reference:* `src/main.py:update_record()`, `app.py:edit_employee_route()`, `src/database.py:update_employee()`.

* **FR-06: Delete Employee Record [Implemented]**
  - *Description:* The system shall remove an employee record from the database after explicit user confirmation.
  - *Processing:* Executes parameterized SQL `DELETE FROM employees WHERE employee_id = ? COLLATE NOCASE`.
  - *Outputs:* Row removed from SQLite; table refreshed; form cleared; success confirmation displayed.
  - *Code Reference:* `src/main.py:delete_record()`, `app.py:delete_employee_route()`, `src/database.py:delete_employee()`.

---

### 6.2 Quality Goal Q06: Duplicate Prevention Requirements

* **FR-07: Case-Insensitive Employee ID Uniqueness [Implemented]**
  - *Description:* The system shall reject insertion of any employee record whose Employee ID matches an existing record under case-insensitive comparison (`E101` == `e101`).
  - *Enforcement:* Table primary key `COLLATE NOCASE`, unique index `idx_employees_id_nocase`, and pre-add lookup.
  - *Outputs:* Rejection error message (`"This employee ID already exists."` or `"Employee ID ... already exists."`); insertion aborted.
  - *Code Reference:* `src/database.py:initialize_database()`, `src/database.py:add_employee()`, `app.py:add_employee_route()`.

* **FR-08: Case-Insensitive Email Address Uniqueness [Implemented]**
  - *Description:* The system shall reject insertion or update of any employee record whose Email address matches an existing record under case-insensitive comparison (`user@domain.com` == `USER@DOMAIN.COM`).
  - *Enforcement:* Column constraint `UNIQUE COLLATE NOCASE` and unique index `idx_employees_email_nocase`.
  - *Outputs:* Rejection error message (`"This email is already registered."`); database unchanged.
  - *Code Reference:* `src/database.py:initialize_database()`, `src/database.py:add_employee()`, `app.py:add_employee_route()`.

* **FR-09: Pre-Add Identifier Verification [Implemented]**
  - *Description:* Prior to presenting a confirmation prompt for a new record, the system shall verify whether the requested Employee ID already exists.
  - *Behavior:* If a duplicate ID is detected, an error alert is presented immediately, and no confirmation prompt is displayed.
  - *Code Reference:* `src/main.py:add_record()`, `app.py:add_employee_route()`.

* **FR-10: Form Key Locking on Edit [Implemented]**
  - *Description:* When editing an existing employee, the Employee ID field shall be rendered immutable (disabled in Tkinter, readonly in Web) to prevent altering the primary key or introducing duplicate identifiers during updates.
  - *Code Reference:* `src/main.py:select_record()`, `templates/edit_employee.html`, `app.py:edit_employee_route()`.

* **FR-11: Update Email Collision Prevention [Implemented]**
  - *Description:* When updating an existing employee's email, the system shall allow retaining or re-casing their own email, but shall strictly reject changing their email to one already registered to a different employee.
  - *Code Reference:* `src/database.py:update_employee()`, `app.py:edit_employee_route()`.

* **FR-12: Mandatory Field Validation [Implemented]**
  - *Description:* The system shall reject any operation where any of the six required employee fields is empty or consists solely of whitespace.
  - *Code Reference:* `src/database.py:add_employee()`, `src/database.py:update_employee()`, `src/main.py:get_form_values()`, `app.py:add_employee_route()`.

* **FR-13: Email Syntax Regex Validation [Implemented]**
  - *Description:* The presentation layers shall validate email format syntax against regex `r"[^@\s]+@[^@\s]+\.[^@\s]+"` before submitting to the database.
  - *Code Reference:* `src/main.py:get_form_values()`, `app.py:add_employee_route()`, `app.py:edit_employee_route()`.

* **FR-14: Modal Confirmation Safeguards [Implemented]**
  - *Description:* Add, update, and delete operations shall require explicit secondary user confirmation via modal dialogs before execution.
  - *Code Reference:* `src/main.py:askyesno`, `templates/add_employee.html`, `templates/edit_employee.html`, `templates/index.html`.

---

### 6.3 Web Interface Specific Requirements

* **FR-15: Web Dashboard and Real-Time KPI Metrics [Implemented]**
  - *Description:* The web dashboard shall compute and display summary metrics (Total Employees, Active Department Count, and Q06 Enforcement Status) alongside the employee table.
  - *Code Reference:* `app.py:index()`, `templates/index.html`.

* **FR-16: Web Poka-Yoke Modals and Form Locking [Implemented]**
  - *Description:* The web interface shall utilize Bootstrap modals for Add, Update, and Delete confirmations. The Edit form shall display the Employee ID with a locked visual style and `readonly` attribute.
  - *Code Reference:* `templates/index.html`, `templates/add_employee.html`, `templates/edit_employee.html`.

* **FR-17: HTTP Method Safeguards [Implemented]**
  - *Description:* The web application shall restrict destructive actions (such as deletion) strictly to HTTP `POST` requests, preventing unintended deletions via GET links or web spiders.
  - *Code Reference:* `app.py:delete_employee_route()`.

---

## 7. Non-Functional Requirements

### 7.1 Data Integrity
* **NFR-01 (Constraint Preservation):** The database engine shall strictly enforce relational integrity and unique constraints on `employee_id` and `email` using ACID-compliant SQLite transactions.
* **NFR-02 (Legacy Compatibility):** Executing `initialize_database()` on clean legacy databases shall preserve all existing employee records and establish case-insensitive unique indexes without data loss.

### 7.2 Reliability
* **NFR-03 (Exception Containment):** Database errors (`sqlite3.IntegrityError`) shall be caught and converted to descriptive domain exceptions (`ValueError`), preventing uncaught application crashes.
* **NFR-04 (Connection Safety):** All database operations shall execute within Python context managers (`@contextmanager`), ensuring connections are closed reliably even when runtime exceptions occur.

### 7.3 Usability
* **NFR-05 (User Feedback):** Operations shall provide immediate feedback via modal dialogs (`messagebox` in Tkinter, Bootstrap alerts/modals in Web).
* **NFR-06 (Keyboard & Search Navigation):** Search supports instant execution via `<Return>` key (Tkinter) and standard form submission (Web).

### 7.4 Maintainability
* **NFR-07 (Modular Separation):** Data persistence logic (`src/database.py`) shall remain decoupled from user interface code (`src/main.py`, `app.py`).
* **NFR-08 (Testability):** All database functions and web routes accept an optional `db_path`, enabling automated testing against isolated temporary databases.

---

## 8. Assumptions, Dependencies, and Limitations

### 8.1 Assumptions
1. Single administrative operator using the software at any given time on a local workstation.
2. English alphanumeric character inputs for employee IDs, names, and email addresses.

### 8.2 Dependencies
* Python 3.10+ runtime with `sqlite3`, `unittest`, and `tkinter` built-in libraries.
* `Flask>=3.0.0` (external dependency specified in `requirements.txt`).
* Bootstrap 5.3.3 and Bootstrap Icons 1.11.3 (served via CDN).

### 8.3 Known Limitations
1. **Conflicting Legacy Database Migration:** If a preexisting legacy database contains duplicate records with differing letter casing, index creation halts with `sqlite3.IntegrityError`. Preexisting records are preserved, but manual deduplication is required before indexes can be established.
2. **CSRF Protection:** Form submissions currently rely on standard HTML forms without CSRF tokens. This design is acceptable for local single-user evaluation but requires CSRF tokens for public multi-user deployments.

---

## 9. Acceptance Criteria (Review 1 & Review 2)

| Review Milestone | Deliverable / Capability | Acceptance Criteria | Current Status |
| :---: | :--- | :--- | :---: |
| **Review 1** | Git Repository Initialization | Local repository initialized, gitignore configured, working tree clean. | **Complete locally** *(Needs push)* |
| **Review 1** | System Architecture Flowchart | Documented flowchart showing data flow between User, Interfaces, and Database. | **Covered in `doc/system-architecture.md`** |
| **Review 1** | Formal SRS Document | Document detailing project objectives, FRs, NFRs, scope, and TQM Q06 alignment. | **Complete in `doc/srs.md`** |
| **Review 1** | Scope Definition | Explicit boundaries identifying in-scope CRUD/Q06 items vs out-of-scope items. | **Complete in `doc/srs.md:Section 5`** |
| **Review 2** | Functional Base CRUD Modules | Working backend functions for Add, View, Search, Update, and Delete with automated tests. | **Complete & Verified (29 tests pass)** |
| **Review 2** | Quality Goal Q06 Execution | Case-insensitive ID/email duplicate prevention, pre-add validation, confirmation prompts. | **Implemented & Verified in DB and Web** |
| **Review 2** | Dual-Interface Availability | Seamless operation of both Tkinter Desktop GUI and Flask Web Application. | **Complete & Verified** |
