# Test Execution Report: Q06 Reduce Duplicate Entries

- **Project:** Employee Management System
- **Course / Module:** BBAT104 — Total Quality Management (TQM)
- **Quality Objective:** Q06 — Reduce Duplicate Entries
- **Author / Student ID:** Riya Mehta (AU-24-5368)
- **Baseline Commit:** `e0e99ab` (Phase 1)
- **Implementation Commit:** `b6ff8be` (Phase 3)
- **Defect Report Reference:** `doc/defect-and-root-cause.md` (Commit `d585b64`)
- **Document Path:** `doc/test-report.md`

---

## 1. Testing Objective and Scope

### Objective
The primary objective of this testing process is to verify the implementation of **TQM Quality Objective Q06: Reduce Duplicate Entries** within the Employee Management System. In accordance with Total Quality Management defect-prevention principles (Poka-Yoke / mistake-proofing), testing evaluates whether the database layer actively prevents duplicate employee records at the point of insertion and update, regardless of letter-casing variations.

### Scope
Testing covers the backend data access layer in `src/database.py`, specifically:
* Database schema creation and migration indexing (`initialize_database`).
* Record creation with duplicate constraint validation (`add_employee`).
* Record retrieval by exact and case-insensitive identifier (`get_employee_by_id`, `get_all_employees`).
* Substring querying across record fields (`search_employees`).
* Record modification with duplicate conflict detection and self-update validation (`update_employee`).
* Record removal by identifier (`delete_employee`).

### Scope Boundary
Automated test execution is strictly confined to the backend database layer (`src/database.py`). The graphical user interface (`src/main.py`) does not currently have automated test coverage. Consequently, this report validates backend data integrity and constraints, and does not claim that the user interface or the overall application is defect-free.

---

## 2. Test Environment and Execution Details

The automated test suite was executed in the following local environment:

* **Operating System:** Windows 11 (64-bit AMD64)
* **Python Runtime:** Python 3.14.6 (MSC v.1944 64-bit)
* **Database Engine:** SQLite 3.50.4 (embedded Python `sqlite3` module)
* **Test Runner:** Python standard library `unittest`
* **Test File:** `tests/test_database.py` (223 lines)
* **Database Isolation:** Every test fixture executes against a dedicated temporary SQLite database file created via `tempfile.TemporaryDirectory()`, ensuring complete isolation with no shared state or cross-test interference.

### Test Execution Command
```powershell
python -m unittest -v tests/test_database.py
```

---

## 3. Automated Test Cases and Execution Results

The test suite in `tests/test_database.py` comprises **15 automated unit test cases**. All 15 tests executed and passed as reported below:

| Test ID | Test Method Name | Category | Test Purpose and Scenario | Expected Result | Actual Result |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | `test_add_and_read_employee` | Baseline CRUD | Add sample employee `E001` and retrieve all stored records via `get_all_employees()`. | Returns a single-item list containing the exact tuple for `E001`. | **PASS** |
| **TC-02** | `test_duplicate_employee_id_is_rejected` | Baseline Q06 | Insert `E001`, then attempt to insert a second record with identical ID `E001`. | Raises `ValueError` matching `"ID already exists"`. | **PASS** |
| **TC-03** | `test_duplicate_email_is_rejected` | Baseline Q06 | Insert `riya@example.com` under `E001`, then attempt to insert same email under `E002`. | Raises `ValueError` matching `"email is already"`. | **PASS** |
| **TC-04** | `test_empty_fields_are_rejected` | Validation | Attempt to insert an employee with a whitespace-only field (`"  "`). | Raises `ValueError` matching `"required"`. | **PASS** |
| **TC-05** | `test_search_employee` | Query | Add `E001` ("Riya Mehta") and search across fields for query substring `"Riya"`. | Returns 1 matching record containing `E001`. | **PASS** |
| **TC-06** | `test_update_employee` | Baseline CRUD | Update existing employee `E001`'s department field to `"Engineering"`. | Field is updated; `get_all_employees()` reflects `"Engineering"`. | **PASS** |
| **TC-07** | `test_delete_employee` | Baseline CRUD | Insert `E001` and delete using exact matching ID `"E001"`. | Record removed; `get_all_employees()` returns empty list `[]`. | **PASS** |
| **TC-08** | `test_duplicate_employee_id_case_insensitive_is_rejected` | Regression Q06 | Insert `E001`, then attempt to insert a second record with lowercase ID `e001`. | Raises `ValueError` matching `"ID already exists"`. | **PASS** |
| **TC-09** | `test_duplicate_email_case_insensitive_is_rejected` | Regression Q06 | Insert `riya@example.com`, then attempt to insert `Riya@Example.Com` under `E002`. | Raises `ValueError` matching `"email is already"`. | **PASS** |
| **TC-10** | `test_get_employee_by_id_case_insensitive` | Regression Query | Insert `E001`, then query via `get_employee_by_id()` with `"E001"` and `"e001"`. | Both queries return the employee record with primary key `"E001"`. | **PASS** |
| **TC-11** | `test_update_employee_rejects_duplicate_email_case_insensitive` | Regression Q06 | Update `E002` to use `RIYA@EXAMPLE.COM` when `E001` already holds `riya@example.com`. | Raises `ValueError` matching `"already registered"`. | **PASS** |
| **TC-12** | `test_update_employee_allows_retaining_own_email` | Update Behavior | Update details for `E001` while passing their existing email `riya@example.com`. | Update succeeds; record values updated without duplicate conflict. | **PASS** |
| **TC-13** | `test_update_employee_allows_casing_change_on_own_email` | Update Behavior | Update `E001`'s email capitalization from `riya@example.com` to `Riya@Example.com`. | Update succeeds; modified capitalization stored without conflict. | **PASS** |
| **TC-14** | `test_delete_employee_case_insensitive` | Regression Delete | Insert record `E001` and delete using lowercase argument `"e001"`. | Record removed; `get_all_employees()` returns empty list `[]`. | **PASS** |
| **TC-15** | `test_legacy_database_backward_compatibility` | Migration | Initialize a clean legacy database (no `COLLATE NOCASE`) containing existing record `E999`. | Existing record preserved; new duplicate `e999` and `Old@EXAMPLE.com` rejected. | **PASS** |

---

## 4. Test Execution Summary

The test run verified by command output:

* **Total Tests Executed:** 15
* **Passed:** 15 (100%)
* **Failed:** 0 (0%)
* **Errors:** 0 (0%)
* **Verified Execution Duration:** 0.449 seconds (from actual captured test run output)

---

## 5. Regression Testing for Case-Insensitive Duplicate Prevention

Prior to commit `b6ff8be`, SQLite's default binary collation permitted case-sensitive duplicate records. The regression suite specifically verifies that the corrective database implementation enforces case-insensitive uniqueness across all standard database interactions:

1. **Insertion Prevention (TC-08, TC-09):**
   * Employee ID uniqueness is enforced via `COLLATE NOCASE` in the primary key and the `idx_employees_id_nocase` index. Inserting `e001` when `E001` exists triggers SQLite constraint failure and raises `ValueError: This employee ID already exists.`
   * Email uniqueness is enforced via `COLLATE NOCASE` in the column constraint and the `idx_employees_email_nocase` index. Inserting `Riya@Example.Com` when `riya@example.com` exists raises `ValueError: This email is already registered.`
2. **Lookup Alignment (TC-10):**
   * `get_employee_by_id()` utilizes `WHERE employee_id = ? COLLATE NOCASE`, ensuring that pre-add checks and user searches find existing records regardless of input casing.
3. **Update Validation and Self-Update Support (TC-11, TC-12, TC-13):**
   * Updating a record to another employee's email with differing letter casing (`RIYA@EXAMPLE.COM`) is caught and rejected with `ValueError: This email is already registered to another employee.`
   * Updating an employee's non-email fields while passing their current email succeeds without false collision.
   * Updating the letter casing of an employee's own email (e.g. normalizing to title case) succeeds without triggering a self-conflict.
4. **Deletion Alignment (TC-14):**
   * `delete_employee()` utilizes `WHERE employee_id = ? COLLATE NOCASE`, ensuring consistent record removal regardless of input letter casing.

---

## 6. Legacy Database Compatibility and Migration Behavior

The system's behavior when interacting with older database files was evaluated through both automated unit testing and separate manual migration verification:

### Automated Test: Clean Legacy Database (TC-15)
* **Scenario:** A legacy SQLite database created using the initial schema (without `COLLATE NOCASE`), containing non-conflicting employee record `E999` (`old@example.com`).
* **Test Verification:** Executing `initialize_database()` on this database:
  1. Preserves existing record `E999` intact and accessible via `get_employee_by_id("e999")`.
  2. Executes `CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_id_nocase` and `idx_employees_email_nocase`.
  3. Rejects new case-variant duplicate insertions (`e999` and `Old@EXAMPLE.com`).
* **Outcome:** Clean legacy databases migrate successfully without data loss or table recreation.

### Separate Manual Verification: Conflicting Legacy Database
* **Scenario:** A legacy SQLite database that *already contains* preexisting case-insensitive duplicate records (for example, both `E001` and `e001`, or both `riya@example.com` and `Riya@example.com`).
* **Observed Empirical Behavior:**
  1. When `initialize_database()` executes `CREATE UNIQUE INDEX`, SQLite detects the conflicting rows and raises `sqlite3.IntegrityError: UNIQUE constraint failed`.
  2. All existing records remain preserved on disk (neither deleted nor merged).
  3. However, index creation halts. Case-insensitive duplicate protection **cannot become active** on that database until an administrator manually resolves or consolidates the preexisting duplicate entries.
* **Important Distinction:** This conflicting-data failure is an expected SQLite engine behavior and a **known migration limitation**. It is documented here from manual verification checks and is **not** an automated test case in `tests/test_database.py`.

---

## 7. Testing Limitations and Recommended Future Tests

### Current Limitations
1. **No Automated GUI Testing:** The desktop application frontend (`src/main.py`) relies on manual verification. Automated tests do not currently cover Tkinter form validation, treeview population, or the dialog sequence (such as the observation noted in `doc/defect-and-root-cause.md` where the confirmation prompt precedes duplicate email validation).
2. **Backend Email Format Validation:** Validation regex for email syntax (`[^@\s]+@[^@\s]+\.[^@\s]+`) resides only in the GUI layer. Calling `add_employee()` directly allows malformed emails if they are non-empty strings.
3. **Demographic / Identity Duplicate Detection:** Automated tests verify uniqueness only for `employee_id` and `email`. The system does not check for soft duplicates where an employee with identical name, department, and city is entered under a new ID and email.

### Recommended Future Tests
1. **GUI Automated Test Suite:** Implement headless UI test cases (e.g., using `unittest.mock` or a Tkinter test driver) to verify form submission flows, error dialog triggers, and field locking.
2. **Backend Format Tests:** Add unit tests validating that `src/database.py` rejects invalid email syntaxes.
3. **Legacy Migration Conflict Detection:** Create automated utility tests for detecting and reporting preexisting duplicate records before attempting index creation.

---

## 8. Conclusion

The 15 automated unit tests in `tests/test_database.py` confirm that the database layer (`src/database.py`) satisfies TQM Quality Objective Q06 by enforcing case-insensitive uniqueness on employee IDs and email addresses, supporting case-insensitive lookups and mutations, and migrating clean legacy databases safely.

While these tests confirm the correctness and stability of the database layer, broader application aspects—specifically GUI workflow sequencing, backend email format enforcement, demographic duplicate detection, and conflicting legacy data remediation—remain outside the scope of the current automated test suite and are recommended for future quality enhancement phases.
