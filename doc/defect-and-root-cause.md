# Defect and Root-Cause Report: Q06 Reduce Duplicate Entries

- **Project:** Employee Management System
- **Course / Module:** BBAT104 — Total Quality Management (TQM)
- **Quality Objective:** Q06 — Reduce Duplicate Entries
- **Author / Student ID:** Riya Mehta (AU-24-5368)
- **Baseline Commit:** `e0e99ab` (Phase 1)
- **Corrective Commit:** `b6ff8be` (Phase 3)
- **Document Path:** `doc/defect-and-root-cause.md`

---

## 1. Project Overview

The Employee Management System is a desktop database application designed to manage employee personnel records. The software consists of a Python graphical user interface built with Tkinter/ttk (`src/main.py`) and a local relational storage layer using SQLite (`src/database.py`).

Within the Total Quality Management (TQM) framework, this project aligns with **Quality Goal Q06: Reduce Duplicate Entries**. In quality management principles, duplicate records represent defects introduced at the input stage. Such defects compromise record integrity, distort administrative reporting, and generate unnecessary operational rework. The goal of Q06 is to implement defect prevention (Poka-Yoke / mistake-proofing) at the database and application levels to ensure records remain accurate and unique.

---

## 2. Problem Statement and Policy Context

### SQLite Default Collation
In standard SQLite schemas, columns declared as `TEXT` use the default `BINARY` collation sequence unless specified otherwise. Binary collation compares string values strictly by byte values (for example, ASCII code `0x45` for `'E'` versus `0x65` for `'e'`). Under this comparison mechanism, strings that differ only in letter casing are evaluated as distinct.

Prior to commit `b6ff8be`, the database schema defined `employee_id TEXT PRIMARY KEY` and `email TEXT NOT NULL UNIQUE` without specifying collation. As a result, values such as `E101` and `e101` satisfied the primary key constraint simultaneously.

### Project-Level Email Case-Sensitivity Policy
In internet protocol standards (such as RFC 5321), the domain part of an email address is case-insensitive, whereas the mailbox local-part technically permits case distinction depending on the destination mail server.

For this Employee Management System, case-insensitive email uniqueness is established strictly as a **project-level data-quality policy**. In this organization's employee directory domain, allowing `riya@example.com` and `Riya@example.com` to exist as distinct employee records constitutes an unintended duplicate entry. Enforcing case-insensitive uniqueness prevents duplicate assignments and operational confusion within this application.

---

## 3. Observed Defects and Behaviors

Through code inspection and isolated empirical testing prior to commit `b6ff8be`, the following defects and behavioral inconsistencies were identified:

### Confirmed Historical Defects

1. **Defect 1: Case-Sensitive Duplicate Employee ID Insertion**
   * *Observation:* An employee with ID `E101` was added to the database. Subsequently, an employee with ID `e101` was also added. Both records were stored simultaneously without error.
   * *Impact:* Redundant records could be created for the same employee identifier when casing differed.

2. **Defect 2: Case-Sensitive Duplicate Email Address Insertion**
   * *Observation:* An employee with email `riya@example.com` was added. A second employee with email `Riya@example.com` was added under a different ID. The database accepted both records without violating the `UNIQUE` constraint.
   * *Impact:* Multiple employee records could be registered with the same functional email address.

3. **Defect 3: Employee Lookup Failure Under Differing Letter Case**
   * *Observation:* When an employee record existed with ID `E001`, invoking `get_employee_by_id("e001")` returned `None`.
   * *Impact:* Retrieval failed when the search casing did not match the stored casing. In `src/main.py:add_record()`, this caused the pre-add check to report that the ID was available, leading to unintended record creation.

4. **Defect 4: Update Allowed Case-Variant Duplicate Email**
   * *Observation:* When employee `E001` held `riya@example.com` and employee `E002` held `aarav@example.com`, updating employee `E002` to `Riya@example.com` succeeded without error.
   * *Impact:* Duplicate emails could be introduced into the system through update operations.

### Identified Behavioral and Workflow Inconsistencies

5. **Behavior 1: Case-Sensitive Record Deletion**
   * *Observation:* In the original implementation, `delete_employee()` executed `DELETE FROM employees WHERE employee_id = ?`. If an operator supplied an ID with casing that differed from the database record, the query affected zero rows. While this matched the original column collation, it was inconsistent with a case-insensitive identifier model and was addressed in Phase 3.

6. **Workflow Defect: GUI Confirmation Dialog Sequence**
   * *Observation:* In `src/main.py:226-237`, `add_record()` checks if the employee ID exists prior to displaying the `"Confirm Addition"` prompt. However, it does not check if the email address already exists. If an existing email is entered, the user is prompted to confirm addition first (`"Add employee [Name]?"`). Only after clicking "Yes" does `add_employee()` run, fail, and display an error alert.
   * *Status:* Confirmed through code inspection; noted as a GUI workflow improvement for a future phase.

---

## 4. Root-Cause Analysis

The technical causes for the observed defects were investigated and categorized into verified technical causes and contributing factors:

### Verified Technical Causes

1. **Default Binary Collation in SQLite Table Schema (`src/database.py`):**
   * `employee_id TEXT PRIMARY KEY` and `email TEXT NOT NULL UNIQUE` were declared without explicit collation. SQLite evaluated uniqueness using byte-level comparison, allowing case-variant duplicates to be inserted.
2. **Binary Equality in ID Lookup and Mutation Queries (`src/database.py`):**
   * Functions `get_employee_by_id()`, `update_employee()`, and `delete_employee()` utilized `WHERE employee_id = ?` without an explicit collation sequence. These queries inherited the column's binary comparison behavior, preventing cross-case matching.
3. **Absence of UI-Accessible Email Lookup Helper (`src/main.py` / `src/database.py`):**
   * The database module did not provide a dedicated lookup helper for email (such as `get_employee_by_email()`). As a result, the GUI author implemented pre-add validation only for the ID, leaving duplicate emails to be caught at database execution time after the confirmation prompt.

### Possible Contributing Factors
* **Specification Form:** The initial schema definition did not explicitly state how identifier casing should be treated across the application layers.
* **Prototyping Focus:** Initial automated tests evaluated only exact-match duplicates, leaving case-insensitivity unexamined in the early testing phase.

---

## 5. Corrective Actions Implemented (Commit `b6ff8be`)

In Phase 3 (commit `b6ff8be`), targeted changes were implemented in `src/database.py` and tested in `tests/test_database.py`:

1. **Schema-Level Case-Insensitive Collation:**
   * Updated `initialize_database()` so that newly initialized tables specify:
     ```sql
     employee_id TEXT PRIMARY KEY COLLATE NOCASE,
     ...
     email TEXT NOT NULL UNIQUE COLLATE NOCASE
     ```
2. **Case-Insensitive Unique Indexes for Legacy Databases:**
   * Because SQLite's `CREATE TABLE IF NOT EXISTS` does not modify columns on preexisting tables, two explicit unique indexes were added to `initialize_database()`:
     ```sql
     CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_id_nocase
     ON employees(employee_id COLLATE NOCASE);

     CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_email_nocase
     ON employees(email COLLATE NOCASE);
     ```
   * On legacy databases that do not contain duplicate records, these indexes enforce case-insensitive uniqueness without requiring table drops or schema reconstruction.
3. **Case-Insensitive Query Matching:**
   * Updated `get_employee_by_id()`, `update_employee()`, and `delete_employee()` to include `WHERE employee_id = ? COLLATE NOCASE`.
   * Updated `get_all_employees()` and `search_employees()` to sort via `ORDER BY employee_id COLLATE NOCASE`.
4. **Integrity Error Mapping:**
   * Updated `add_employee()` exception handling to inspect the error string for both column names and the index names (`idx_employees_id_nocase`, `idx_employees_email_nocase`), ensuring consistent mapping of SQLite errors to user-facing `ValueError` messages.
5. **Self-Update Support:**
   * Verified that SQLite allows an employee to retain their own email or change its capitalization during an update, while rejecting changes that duplicate another employee's email.

---

## 6. Defect and Improvement Matrix

| Item ID | Classification | Description | Technical Root Cause | Corrective Action | Verification Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | Confirmed Defect | Case-sensitive duplicate employee IDs allowed (`E001` vs `e001`) | SQLite default `BINARY` collation on `TEXT PRIMARY KEY` | Added `COLLATE NOCASE` and `idx_employees_id_nocase` index | `test_duplicate_employee_id_case_insensitive_is_rejected` (PASS) |
| **DEF-02** | Confirmed Defect | Case-sensitive duplicate emails allowed (`user@a.com` vs `User@a.com`) | SQLite default `BINARY` collation on `TEXT NOT NULL UNIQUE` | Added `COLLATE NOCASE` and `idx_employees_email_nocase` index | `test_duplicate_email_case_insensitive_is_rejected` (PASS) |
| **DEF-03** | Confirmed Defect | `get_employee_by_id()` failed when search case differed from stored case | `WHERE employee_id = ?` used binary matching | Added `COLLATE NOCASE` to SQL `WHERE` clause | `test_get_employee_by_id_case_insensitive` (PASS) |
| **DEF-04** | Confirmed Defect | Updating email permitted taking another employee's email with different casing | Email unique constraint lacked case-insensitive collation | Unique index enforces case-insensitive uniqueness on update | `test_update_employee_rejects_duplicate_email_case_insensitive` (PASS) |
| **BEH-01** | Behavior Corrected | Deletion by ID failed if input case differed from stored record | `DELETE ... WHERE employee_id = ?` used binary matching | Added `COLLATE NOCASE` to `DELETE` statement | `test_delete_employee_case_insensitive` (PASS) |
| **IMP-01** | Pending Improvement | GUI prompts user confirmation before checking for duplicate email | `add_record()` lacks email pre-check before `askyesno()` | Documented for future phase GUI refinement | Confirmed via inspection of `src/main.py:226-237` |

---

## 7. Verification Evidence

The test suite in `tests/test_database.py` contains **15 automated unit tests**, executed against isolated temporary databases using Python's standard `unittest` runner.

### Test Execution Command:
```powershell
python -m unittest -v tests/test_database.py
```

### Verified Test Cases:

| # | Test Method Name | Origin | Target Behavior | Result |
| :-: | :--- | :--- | :--- | :-: |
| 1 | `test_add_and_read_employee` | Phase 1 Baseline | Record insertion and retrieval via `get_all_employees()`. | **PASS** |
| 2 | `test_duplicate_employee_id_is_rejected` | Phase 1 Baseline | Exact-case duplicate employee ID insertion raises `ValueError`. | **PASS** |
| 3 | `test_duplicate_email_is_rejected` | Phase 1 Baseline | Exact-case duplicate email insertion raises `ValueError`. | **PASS** |
| 4 | `test_empty_fields_are_rejected` | Phase 1 Baseline | Empty or whitespace-only fields are rejected. | **PASS** |
| 5 | `test_search_employee` | Phase 1 Baseline | Substring search across employee fields. | **PASS** |
| 6 | `test_update_employee` | Phase 1 Baseline | Updating employee details for an existing record. | **PASS** |
| 7 | `test_delete_employee` | Phase 1 Baseline | Deleting an employee by exact ID. | **PASS** |
| 8 | `test_duplicate_employee_id_case_insensitive_is_rejected` | Phase 3 Addition | Adding `e001` when `E001` exists raises `ValueError`. | **PASS** |
| 9 | `test_duplicate_email_case_insensitive_is_rejected` | Phase 3 Addition | Adding `Riya@Example.Com` when `riya@example.com` exists raises `ValueError`. | **PASS** |
| 10 | `test_get_employee_by_id_case_insensitive` | Phase 3 Addition | `get_employee_by_id()` retrieves record `E001` when queried with `"e001"`. | **PASS** |
| 11 | `test_update_employee_rejects_duplicate_email_case_insensitive` | Phase 3 Addition | Updating `E002` to `RIYA@EXAMPLE.COM` when `E001` owns `riya@example.com` raises `ValueError`. | **PASS** |
| 12 | `test_update_employee_allows_retaining_own_email` | Phase 3 Addition | Updating other fields while passing the same email succeeds without conflict. | **PASS** |
| 13 | `test_update_employee_allows_casing_change_on_own_email` | Phase 3 Addition | Updating own email casing (e.g. `riya@example.com` to `Riya@Example.com`) succeeds. | **PASS** |
| 14 | `test_delete_employee_case_insensitive` | Phase 3 Addition | Deleting by lowercase ID `"e001"` successfully removes record `"E001"`. | **PASS** |
| 15 | `test_legacy_database_backward_compatibility` | Phase 3 Addition | Initializing a legacy database preserves existing records and blocks new case-insensitive duplicates. | **PASS** |

*Summary:* All 15 unit tests passed with 0 failures and 0 errors.

---

## 8. Limitations and Remaining Risks

1. **Legacy Databases Containing Conflicting Records:**
   * **Clean legacy database:** If an existing database contains no case-insensitive duplicate records, `initialize_database()` succeeds and creates the unique indexes.
   * **Conflicting legacy database:** If an existing database already contains conflicting records (such as both `E001` and `e001`, or duplicate emails), index creation fails with `sqlite3.IntegrityError`.
   * **Handling:** In such cases, existing records are preserved and neither deleted nor merged. However, duplicate protection cannot become active until conflicting data is resolved manually by an administrator. Not all legacy databases will migrate automatically.
2. **Demographic / Identity Duplicate Entries:**
   * The current implementation enforces uniqueness only on `employee_id` and `email`. It does not detect duplicate human entities entered with a different ID and email (e.g. identical First Name, Last Name, Department, and City).
3. **Backend Email Format Validation:**
   * Email syntax regex validation is enforced in the GUI (`src/main.py`), but not in `src/database.py`. Direct backend calls can insert non-empty strings that do not conform to standard email formatting.
4. **GUI Confirmation Workflow:**
   * The confirmation dialog in `src/main.py` continues to appear before checking email uniqueness, which remains to be addressed in a subsequent phase.

---

## 9. Conclusion

The database layer changes in commit `b6ff8be` enforce case-insensitive uniqueness for employee IDs and email addresses, and align lookup, update, and deletion queries to operate consistently across letter casing variations. These improvements are validated by the 15 automated tests in `tests/test_database.py`.

These changes resolve the specific case-sensitivity issues targeted in Phase 3. However, they do not make the entire application defect-free. Broader quality aspects—including GUI validation sequencing, demographic similarity checks, backend format validation, and conflicting legacy data migration—remain outside the scope of the current tests and warrant further engineering in subsequent phases.
