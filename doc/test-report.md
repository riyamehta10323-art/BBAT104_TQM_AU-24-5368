# Test Execution Report: Q06 Reduce Duplicate Entries
## Dual-Interface Test Suite (Database & Web Routes)

- **Project:** Employee Management System
- **Course / Module:** BBAT104 — Total Quality Management (TQM)
- **Quality Objective:** Q06 — Reduce Duplicate Entries
- **Author / Student ID:** Riya Mehta (AU-24-5368)
- **Baseline Commit:** `e0e99ab` (Phase 1)
- **Corrective Commit:** `b6ff8be` (Phase 3)
- **Defect Report Reference:** `doc/defect-and-root-cause.md` (Commit `d585b64`)
- **Document Path:** `doc/test-report.md`

---

## 1. Testing Objective and Scope

### Objective
The primary objective of this testing process is to verify the implementation of **TQM Quality Objective Q06: Reduce Duplicate Entries** across both the backend database layer and the Flask web presentation layer. In accordance with Total Quality Management defect-prevention principles (Poka-Yoke / mistake-proofing), testing evaluates whether:
1. The database layer actively prevents duplicate employee records at the point of insertion and update, regardless of letter-casing variations.
2. The web application enforces client and server-side validation, rejects duplicate IDs and emails with descriptive flash alerts, locks primary keys during edits, and restricts destructive actions to HTTP `POST`.

### Scope
Testing covers two automated test suites:
1. **Backend Relational Layer (`tests/test_database.py`):**
   * Schema initialization and backwards-compatible index creation (`initialize_database`).
   * Record creation with duplicate constraint validation (`add_employee`).
   * Record retrieval by exact and case-insensitive identifier (`get_employee_by_id`, `get_all_employees`).
   * Substring querying across record fields (`search_employees`).
   * Record modification with duplicate conflict detection and self-update validation (`update_employee`).
   * Record removal by identifier (`delete_employee`).
2. **Web Presentation & Route Layer (`tests/test_web.py`):**
   * Dashboard and form rendering (`GET /`, `GET /add`, `GET /edit/<id>`).
   * Search filtering via query parameters (`GET /?search=...`).
   * Form validation (empty-field rejection, regex email syntax checks).
   * Web-tier case-insensitive duplicate ID and email rejection.
   * Form key locking on edit (readonly primary key attribute).
   * Safe employee updates and email collision blocking.
   * Safe record deletion via HTTP `POST /delete/<id>`.

### Scope Boundary
Automated test execution covers the backend database layer (`src/database.py`) and the Flask web application routes (`app.py`). The desktop graphical user interface (`src/main.py`) relies on manual verification.

---

## 2. Test Environment and Execution Details

The automated test suite was executed in the following local environment:

* **Operating System:** Windows 11 (64-bit AMD64)
* **Python Runtime:** Python 3.14.6 (MSC v.1944 64-bit)
* **Web Framework:** Flask 3.1.3 (Jinja2 3.1.6, Werkzeug 3.1.9)
* **Database Engine:** SQLite 3.50.4 (embedded Python `sqlite3` module)
* **Test Runner:** Python standard library `unittest`
* **Test Suites:**
  * `tests/test_database.py` (15 test methods)
  * `tests/test_web.py` (14 test methods)
* **Database Isolation:** Every test fixture executes against a dedicated temporary SQLite database file created via `tempfile.TemporaryDirectory()`, ensuring complete isolation with no shared state or cross-test interference. The production database (`employees.db`) is never modified by test execution.

### Test Execution Commands
```powershell
# Run the complete test suite (all 29 tests)
python -m unittest discover -s tests -v

# Run backend database unit tests (15 tests)
python -m unittest -v tests/test_database.py

# Run web application route tests (14 tests)
python -m unittest -v tests/test_web.py
```

---

## 3. Automated Test Cases and Execution Results

The automated test suite comprises **29 automated test cases** (TC-01 through TC-29). All 29 tests executed and passed as reported below:

### Part A: Backend Database Unit Tests (`tests/test_database.py`)

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

### Part B: Web Application Route Tests (`tests/test_web.py`)

| Test ID | Test Method Name | Category | Test Purpose and Scenario | Expected Result | Actual Result |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-16** | `test_dashboard_loads_successfully` | Web Navigation | Send `GET /` to request the main web dashboard. | Status 200 OK; renders title, KPI cards, and employee table. | **PASS** |
| **TC-17** | `test_add_page_loads_successfully` | Web Navigation | Send `GET /add` to request the Add Employee form. | Status 200 OK; renders form inputs and Q06 integrity rules callout. | **PASS** |
| **TC-18** | `test_add_employee_success` | Web CRUD | Send `POST /add` with valid payload (`E100`, John Doe, IT, etc.). | Status 200 (redirect followed); flashes success; persists in SQLite. | **PASS** |
| **TC-19** | `test_add_employee_missing_fields_rejected` | Web Validation | Send `POST /add` with blank `first_name`. | Status 400 Bad Request; flashes `"All employee fields are required"`. | **PASS** |
| **TC-20** | `test_add_employee_invalid_email_regex_rejected` | Web Validation | Send `POST /add` with malformed email syntax (`invalid-email-address`). | Status 400 Bad Request; flashes `"Please enter a valid email address"`. | **PASS** |
| **TC-21** | `test_add_duplicate_employee_id_case_insensitive_rejected` | Web Q06 | Insert `E001`, then send `POST /add` with lowercase ID `e001`. | Status 400 Bad Request; flashes `"already exists"`; insert blocked. | **PASS** |
| **TC-22** | `test_add_duplicate_email_case_insensitive_rejected` | Web Q06 | Insert `E001` (`riya@example.com`), then send `POST /add` with `RIYA@EXAMPLE.COM`. | Status 400 Bad Request; flashes `"already registered"`; insert blocked. | **PASS** |
| **TC-23** | `test_search_employees_route` | Web Query | Add `E001` and `E002` ("Amit"), send `GET /?search=Amit`. | Status 200 OK; filtered view contains `Amit`; excludes non-matches. | **PASS** |
| **TC-24** | `test_edit_page_loads_with_locked_id` | Web Poka-Yoke | Send `GET /edit/E001` to view edit form. | Status 200 OK; form pre-filled; ID has `readonly` attribute and locked styling. | **PASS** |
| **TC-25** | `test_edit_employee_post_updates_record` | Web CRUD | Send `POST /edit/E001` updating department to `"Quality Assurance"`. | Status 200 (redirect followed); flashes success; SQLite updated. | **PASS** |
| **TC-26** | `test_edit_employee_missing_fields_rejected` | Web Validation | Send `POST /edit/E001` with empty `first_name`. | Status 400 Bad Request; flashes required error; original record intact. | **PASS** |
| **TC-27** | `test_edit_employee_invalid_email_regex_rejected` | Web Validation | Send `POST /edit/E001` with invalid email string (`invalid-email-format`). | Status 400 Bad Request; flashes email syntax error; original email preserved. | **PASS** |
| **TC-28** | `test_edit_employee_duplicate_email_rejected` | Web Q06 | Edit `E002` to use `E001`'s email (`FIRST@EXAMPLE.COM`). | Status 400 Bad Request; flashes `"already registered to another employee"`. | **PASS** |
| **TC-29** | `test_delete_employee_success` | Web CRUD | Send `POST /delete/E001` to remove record. | Status 200 (redirect followed); flashes success; record removed from SQLite. | **PASS** |

---

## 4. Test Execution Summary

Verified test run by command output:

* **Total Tests Executed:** **29**
* **Passed:** **29 (100%)**
* **Failed:** **0 (0%)**
* **Errors:** **0 (0%)**
* **Verified Execution Duration:** **0.957 seconds** (captured from test runner output)

---

## 5. Regression Testing for Case-Insensitive Duplicate Prevention

Prior to commit `b6ff8be`, SQLite's default binary collation permitted case-sensitive duplicate records. The combined regression suite verifies that the corrective implementation enforces case-insensitive uniqueness across all layers:

1. **Insertion Prevention (TC-08, TC-09, TC-21, TC-22):**
   * Employee ID uniqueness is enforced via `COLLATE NOCASE` in the primary key, the `idx_employees_id_nocase` index, and pre-add lookup. Inserting `e001` when `E001` exists triggers failure and returns clear user alerts.
   * Email uniqueness is enforced via `COLLATE NOCASE` in the column constraint and the `idx_employees_email_nocase` index. Inserting `RIYA@EXAMPLE.COM` when `riya@example.com` exists is rejected.
2. **Lookup Alignment (TC-10, TC-23):**
   * `get_employee_by_id()` utilizes `WHERE employee_id = ? COLLATE NOCASE`, ensuring lookups find existing records regardless of input casing.
   * `search_employees()` enables case-insensitive substring matching across all fields.
3. **Update Validation and Self-Update Support (TC-11, TC-12, TC-13, TC-28):**
   * Updating a record to another employee's email with differing letter casing (`FIRST@EXAMPLE.COM`) is caught and rejected.
   * Updating an employee's non-email fields while retaining their current email succeeds without false collision.
   * Updating the letter casing of an employee's own email succeeds without triggering a self-conflict.
4. **Deletion Alignment (TC-14, TC-29):**
   * `delete_employee()` utilizes `WHERE employee_id = ? COLLATE NOCASE`, ensuring consistent record removal regardless of input letter casing.

---

## 6. Legacy Database Compatibility and Migration Behavior

The system's behavior when interacting with older database files was evaluated through automated unit testing (TC-15) and separate manual migration verification:

### Automated Test: Clean Legacy Database (TC-15)
* **Scenario:** A legacy SQLite database created using the initial schema (without `COLLATE NOCASE`), containing non-conflicting employee record `E999` (`old@example.com`).
* **Test Verification:** Executing `initialize_database()`:
  1. Preserves existing record `E999` intact and accessible via `get_employee_by_id("e999")`.
  2. Creates fallback unique indexes `idx_employees_id_nocase` and `idx_employees_email_nocase`.
  3. Rejects new case-variant duplicate insertions (`e999` and `Old@EXAMPLE.com`).
* **Outcome:** Clean legacy databases migrate successfully without data loss or table recreation.

### Separate Manual Verification: Conflicting Legacy Database
* **Scenario:** A legacy SQLite database that *already contains* preexisting case-insensitive duplicate records (e.g. both `E001` and `e001`).
* **Observed Empirical Behavior:** SQLite raises `sqlite3.IntegrityError: UNIQUE constraint failed` during index creation. All existing records remain preserved on disk, but index creation halts until an administrator manually reconciles the conflicting records. This is a documented SQLite engine behavior and migration boundary.

---

## 7. Testing Limitations and Security Boundaries

1. **Desktop GUI Automation:** The desktop application frontend (`src/main.py`) relies on manual verification. The web application frontend has full automated route test coverage (TC-16 through TC-29).
2. **CSRF Protection Boundary:** Form submissions currently rely on standard HTML forms without CSRF tokens. This design is appropriate for local single-user evaluation and academic demonstrations, but public multi-user deployments require CSRF tokens (e.g., using `Flask-WTF`).
3. **Demographic Duplicate Detection:** Automated tests verify uniqueness for `employee_id` and `email`. The system does not check for soft duplicates where an employee with identical name, department, and city is entered under a new ID and email.

---

## 8. Conclusion

The 29 automated test cases across `tests/test_database.py` and `tests/test_web.py` confirm that both the relational database layer and the Flask web application satisfy TQM Quality Objective Q06 by enforcing case-insensitive uniqueness, validating input formats, locking immutable keys, and safeguarding data operations across both desktop and web interfaces.
