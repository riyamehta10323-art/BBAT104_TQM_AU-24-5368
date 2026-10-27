# TQM KPI Evidence — Q06

**Project:** Employee Management System  
**Quality Objective:** Q06 — Reduce Duplicate Entries

## 1. Quality Goal

Prevent duplicate employee IDs and email addresses, including case variations, to maintain data integrity.

## 2. KPI Definition

**Duplicate Rejection Rate**

Duplicate Rejection Rate = (Number of duplicate-entry attempts rejected / Total duplicate-entry attempts tested) × 100

**Target:** 100% of tested duplicate-entry attempts should be rejected.

**Observed result:** A duplicate employee ID was previously tested and rejected by the application. The database also contains dedicated unique indexes for employee ID and email. The final numerical rejection rate will be reported after counting the relevant verified test cases in the test report.

## 3. Supporting Evidence

- `../test-report.md` — Automated test results.
- `../defect-and-root-cause.md` — Defect and root-cause documentation.
- `../erd.png` — Employee database structure.
- Application screenshots stored in this evidence folder.

## 4. Verification

The application uses database-level unique indexes to prevent duplicate employee IDs and email addresses. Case-insensitive rejection is part of the Q06 quality objective and should be supported by the corresponding test cases.

## 5. Conclusion

The project incorporates duplicate-entry prevention at the database level and user-facing validation. Verified test results and application screenshots provide evidence for evaluating the Q06 quality objective.