# Software Requirements Specification (SRS)
## Employee Management System — Q06: Reduce Duplicate Entries

- **Course:** BBAT104 — Total Quality Management (TQM)
- **Quality Objective:** Q06 — Reduce Duplicate Entries
- **Author / Student ID:** Riya Mehta (AU-24-5368)
- **Document Version:** 1.0 (Review 1 Deliverable)
- **Document Path:** `doc/srs.md`
- **Related Documents:** `doc/system-architecture.md`, `doc/defect-and-root-cause.md`, `doc/test-report.md`

---

## 1. Introduction and Purpose

### 1.1 Purpose
This Software Requirements Specification (SRS) document details the functional, non-functional, and quality requirements for the **Employee Management System (EMS)**. It serves as the baseline for Review 1 (Setup & SRS) and Review 2 (Base System & CRUD) in the BBAT104 Total Quality Management course curriculum.

### 1.2 Document Conventions
* **FR-xx**: Functional Requirement identifier.
* **NFR-xx**: Non-Functional Requirement identifier.
* Requirements marked **[Implemented]** reflect verified behaviors in the current codebase (`src/database.py`, `src/main.py`).
* Requirements marked **[Planned Improvement]** indicate recognized enhancement opportunities identified during quality audits for future phases.

### 1.3 Intended Audience
* Course faculty and external evaluators assessing Review 1 and Review 2 criteria.
* The student developer responsible for implementation, testing, and maintenance.

---

## 2. Project Objectives & TQM Context

### 2.1 Project Goal
The primary objective of the Employee Management System is to provide a reliable, desktop-based record management solution that maintains organized personnel data while preventing dirty, inaccurate, or redundant employee entries.

### 2.2 TQM Quality Goal Q06: Reduce Duplicate Entries
In Total Quality Management (TQM) and data quality engineering, duplicate records are categorized as **input-stage defects**. Unchecked duplicate entries introduce significant organizational friction:
* Inaccurate headcount calculations and flawed personnel metrics.
* Payroll errors and split performance records.
* Communication breakdowns resulting from redundant or divergent contact addresses.
* Excessive human overhead spent manually auditing and reconciling conflicting entries.

### 2.3 Poka-Yoke (Mistake-Proofing) Principle
Under traditional data management, duplicate entries are cleaned up through periodic post-hoc audits (defect detection). Under TQM, the system implements **Poka-Yoke (defect prevention at the source)**. The application is structured so that accidental duplicate entries—whether due to exact re-entry, casing variations, or premature confirmation—are intercepted and prevented before they can be committed to persistent storage.

---

## 3. Existing System Overview & Technology Stack

### 3.1 System Overview
The system is implemented as a two-tier desktop architecture:
1. **Frontend Presentation & Event Handling (`src/main.py`):** Built with Python's standard `tkinter` and `ttk` library. Provides an interactive form, action buttons, search bar, scrollable Treeview table, and modal confirmation dialogs.
2. **Backend Storage & Data Access (`src/database.py`):** Uses Python's standard `sqlite3` library to execute relational storage operations, manage database connections, and enforce relational constraints.

### 3.2 Technology Stack
* **Programming Language:** Python 3 (verified on Python 3.14.6 64-bit)
* **GUI Toolkit:** Tkinter / TTK (standard library)
* **Database Engine:** SQLite 3 (verified on SQLite 3.50.4)
* **Test Runner:** Python standard library `unittest`
* **Development & Version Control:** Visual Studio Code, Git, GitHub

### 3.3 System Constraints
* **Single-User Desktop Environment:** The software executes locally as a single-user desktop application; it is not architected as a concurrent multi-tenant client-server system.
* **Local Persistent Storage:** All records persist in a single local database file (`employees.db`) in the project directory.

---

## 4. User Characteristics and User Interactions

### 4.1 Intended Users
The intended primary user is a human resources assistant, administrative clerk, or departmental operator responsible for maintaining employee records within an organization. Users possess basic computer literacy and operate through graphical form controls (mouse clicks and standard keyboard inputs).

### 4.2 Standard User Workflows
1. **Adding an Employee:** User fills form fields, clicks "Add Employee", responds to the confirmation prompt, and views the updated table upon success.
2. **Searching Employees:** User enters a search query in the search bar, clicks "Search" (or presses Enter), and views filtered records. Clicking "Show All" resets the view.
3. **Updating an Employee:** User clicks an employee row in the table (which locks the Employee ID and populates fields), modifies editable fields, clicks "Update Selected", and confirms the action.
4. **Deleting an Employee:** User selects an employee row, clicks "Delete Selected", and confirms the destructive deletion dialog.
5. **Form Clearing:** User clicks "Clear Form" to reset input entries and restore the Employee ID field to an editable state.

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
  - Case-insensitive uniqueness enforcement (`COLLATE NOCASE` and unique indexes).
  - Pre-add duplicate ID check in the user interface.
  - Form field locking (ID field disabled during selection) to prevent duplicate key creation on update.
  - User confirmation dialogs (`askyesno`) for add, update, and delete actions.
  - Mandatory non-empty validation for all six fields.
  - GUI email syntax format validation using regular expressions.
* **Local SQLite Relational Storage:** Automated database and index creation (`initialize_database`).
* **Automated Regression Suite:** Unit testing covering database constraints and CRUD operations.

### 5.2 Out-of-Scope Items
* Multi-user concurrent networking and distributed client-server APIs.
* User authentication, role-based access control (RBAC), and session management.
* Biometric authentication or automated employee identity card scanning.
* Cloud synchronization and enterprise ERP / payroll system integration.
* Automated phonetic or machine-learning-based demographic fuzzy matching (e.g. soundex matching for human names).

---

## 6. Functional Requirements

### 6.1 Base CRUD Operations

* **FR-01: Add Employee Record [Implemented]**
  - *Description:* The system shall allow the operator to create a new employee record by providing Employee ID, First Name, Last Name, Department, Email, and City.
  - *Inputs:* Six text strings via GUI form entries.
  - *Processing:* Inputs are trimmed of leading/trailing whitespace. The system validates that all fields are non-empty, checks email syntax, verifies that the ID does not already exist, prompts for user confirmation, and commits the row to SQLite.
  - *Outputs:* Record inserted into database; Treeview refreshed; form cleared; success confirmation displayed.

* **FR-02: View Employee Directory [Implemented]**
  - *Description:* The system shall display all stored employee records in a scrollable, multi-column tabular view (Treeview).
  - *Processing:* Records are retrieved using `SELECT ... ORDER BY employee_id COLLATE NOCASE`.
  - *Outputs:* Formatted table showing Employee ID, First Name, Last Name, Department, Email, and City.

* **FR-03: Search Employee Records [Implemented]**
  - *Description:* The system shall allow operators to filter the directory by entering a search term.
  - *Processing:* Backend executes a SQL wildcard query matching the search term across all six columns using `LIKE %query%`. Searching is triggered via the "Search" button or pressing the `<Return>` key.
  - *Outputs:* Treeview updates to show only matching records; status bar reports search count.

* **FR-04: Update Existing Employee Record [Implemented]**
  - *Description:* The system shall permit operators to modify the First Name, Last Name, Department, Email, and City of a selected employee.
  - *Processing:* The target employee ID is matched case-insensitively (`WHERE employee_id = ? COLLATE NOCASE`). The system prevents changing another employee's email to a duplicate address, but allows an employee to retain their own email.
  - *Outputs:* Record updated in database; table refreshed; form cleared; success notification shown.

* **FR-05: Delete Employee Record [Implemented]**
  - *Description:* The system shall allow operators to permanently delete a selected employee record.
  - *Processing:* System matches target ID case-insensitively (`WHERE employee_id = ? COLLATE NOCASE`) and deletes the record upon explicit confirmation.
  - *Outputs:* Record removed from database; table refreshed; form cleared; confirmation notification shown.

* **FR-06: Clear Input Form [Implemented]**
  - *Description:* The system shall provide a "Clear Form" action that clears all text inputs, unselects any highlighted table row, restores the Employee ID field state to normal, and updates the status bar.

---

### 6.2 Duplicate Entry Prevention Requirements (Quality Goal Q06)

* **FR-07: Unique Employee ID Enforcement [Implemented]**
  - *Description:* The system shall enforce that every `employee_id` is unique across all database rows.
  - *Mechanism:* SQLite `employee_id TEXT PRIMARY KEY COLLATE NOCASE` and unique index `idx_employees_id_nocase`.
  - *Response:* Any attempt to insert an existing employee ID shall raise a `ValueError` with `"This employee ID already exists."`

* **FR-08: Unique Email Address Enforcement [Implemented]**
  - *Description:* The system shall enforce that every `email` is unique across all database rows.
  - *Mechanism:* SQLite `email TEXT NOT NULL UNIQUE COLLATE NOCASE` and unique index `idx_employees_email_nocase`.
  - *Response:* Any attempt to insert or update to an existing email address shall raise a `ValueError` with `"This email is already registered."` or `"This email is already registered to another employee."`

* **FR-09: Case-Insensitive Duplicate Interception [Implemented]**
  - *Description:* The system shall treat identifiers differing only in letter case as duplicates (e.g. `E101` and `e101`, or `user@example.com` and `USER@EXAMPLE.COM`).
  - *Mechanism:* SQLite column collation `COLLATE NOCASE` and index expressions `ON employees(employee_id COLLATE NOCASE)` and `ON employees(email COLLATE NOCASE)`.

* **FR-10: Form Key Locking on Selection [Implemented]**
  - *Description:* When an employee record is selected from the table for editing, the system shall disable the `Employee ID` form field (`state="disabled"`).
  - *Purpose:* Prevents the operator from inadvertently modifying the entity key or creating duplicate cloned records during update workflows.

---

### 6.3 Input Validation and Dialog Sequencing

* **FR-11: Mandatory Field Validation [Implemented]**
  - *Description:* All six employee fields must contain non-whitespace characters.
  - *Mechanism:* Handled at both GUI layer (`get_form_values()`) and database layer (`add_employee()`, `update_employee()`). Blank inputs raise `"Please fill in all six fields."` / `"All employee fields are required."`

* **FR-12: Email Syntax Format Validation [Implemented in GUI]**
  - *Description:* The GUI shall validate that the email field contains a valid address structure matching `r"[^@\s]+@[^@\s]+\.[^@\s]+"`.
  - *Boundary:* Enforced in `src/main.py:get_form_values()`. Direct calls to `src/database.py` do not perform regex validation.

* **FR-13: Pre-Add Identifier Check [Implemented in GUI]**
  - *Description:* Prior to opening the addition confirmation dialog, the GUI shall query the database using `get_employee_by_id(employee_id)`. If the ID exists, the process halts immediately with an error dialog.

* **FR-14: Explicit User Confirmation Prompts [Implemented in GUI]**
  - *Description:* Destructive or persistent actions (Add, Update, Delete) shall display a modal confirmation popup (`messagebox.askyesno`) requiring explicit user approval before execution.

---

### 6.4 Differentiating Implemented Functionality from Planned Improvements

| Requirement Item | Implementation State | Current Code Status | Planned Improvement |
| :--- | :---: | :--- | :--- |
| **Case-Insensitive ID & Email Uniqueness** | **Implemented** | Active in `src/database.py` and verified by 15 tests. | None; complete for core scope. |
| **Pre-Add Email Check in GUI** | **Planned Improvement** | In `src/main.py:add_record()`, ID is checked before confirmation dialog, but email uniqueness is checked only at insert time. | Add pre-add email uniqueness check before displaying confirmation popup. |
| **Backend Email Syntax Validation** | **Planned Improvement** | Enforced in `src/main.py` via regex; `src/database.py` accepts any non-empty string. | Add email regex validation directly within `src/database.py`. |
| **Demographic Duplicate Detection** | **Planned Improvement** | System checks only ID and email uniqueness. | Implement soft warning dialog if matching First Name + Last Name + City exists under a new ID. |

---

## 7. Non-Functional Requirements

### 7.1 Data Integrity
* **NFR-01 (Constraint Preservation):** The database engine shall strictly enforce relational integrity and unique constraints on `employee_id` and `email` using ACID-compliant SQLite transactions.
* **NFR-02 (Legacy Compatibility):** Executing `initialize_database()` on clean legacy databases shall preserve all existing employee records and establish case-insensitive unique indexes without data loss.

### 7.2 Reliability
* **NFR-03 (Exception Containment):** Database errors (such as `sqlite3.IntegrityError`) shall be caught and converted to descriptive domain exceptions (`ValueError`), preventing uncaught application crashes.
* **NFR-04 (Connection Safety):** All database operations shall execute within Python context managers (`@contextmanager`), ensuring connections are closed reliably even when runtime exceptions occur.

### 7.3 Usability
* **NFR-05 (User Feedback):** Operations shall provide immediate feedback via modal dialogs (`messagebox.showinfo`, `messagebox.showerror`, `messagebox.showwarning`) and a bottom status bar.
* **NFR-06 (Keyboard Navigation):** The search interface shall support keyboard execution via the `<Return>` key.

### 7.4 Maintainability
* **NFR-07 (Modular Separation):** Data persistence logic (`src/database.py`) shall remain decoupled from user interface code (`src/main.py`).
* **NFR-08 (Testability):** All database functions shall accept an optional `db_path` parameter, enabling automated testing against isolated temporary databases.

---

## 8. Assumptions, Dependencies, and Limitations

### 8.1 Assumptions
1. Single administrative operator using the software at any given time on a local workstation.
2. English alphanumeric character inputs for employee IDs, names, and email addresses.

### 8.2 Dependencies
* Standard Python 3.10+ runtime with `tkinter` and `sqlite3` built-in libraries.
* Local filesystem read/write permissions in the repository directory.

### 8.3 Known Limitations
1. **Conflicting Legacy Database Migration:** If a preexisting legacy database already contains duplicate records with differing letter casing (e.g. both `E001` and `e001`), index creation fails with `sqlite3.IntegrityError`. Preexisting records are preserved, but manual deduplication by an administrator is required before unique indexes can be created.
2. **GUI Testing Scope:** Automated test execution is currently confined to `tests/test_database.py`. The GUI in `src/main.py` has not been automated via a headless test framework and relies on manual execution.

---

## 9. Acceptance Criteria (Review 1 & Review 2)

| Review Milestone | Deliverable / Capability | Acceptance Criteria | Current Status |
| :---: | :--- | :--- | :---: |
| **Review 1** | Git Repository Initialization | Local repository initialized, gitignore configured, working tree clean. | **Complete locally** *(Needs push)* |
| **Review 1** | System Architecture Flowchart | Documented flowchart showing data flow between User, GUI, and Database. | **Covered in `doc/system-architecture.md`** |
| **Review 1** | Formal SRS Document | Document detailing project objectives, FRs, NFRs, scope, and TQM Q06 alignment. | **Complete in `doc/srs.md`** |
| **Review 1** | Scope Definition | Explicit boundaries identifying in-scope CRUD/Q06 items vs out-of-scope items. | **Complete in `doc/srs.md:Section 5`** |
| **Review 2** | Functional Base CRUD Modules | Working backend functions for Add, View, Search, Update, and Delete with automated tests. | **Complete & Verified (15 tests pass)** |
| **Review 2** | Quality Goal Q06 Execution | Case-insensitive ID/email duplicate prevention, pre-add validation, confirmation prompts. | **Implemented & Verified in DB** |
