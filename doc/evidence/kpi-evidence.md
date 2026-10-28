# TQM KPI Evidence — Q06

**Project:** Employee Management System  
**Quality Objective:** Q06 — Reduce Duplicate Entries

## 1. Quality Goal

Prevent duplicate employee IDs and email addresses, including case variations, to maintain data integrity.

## 2. KPI Definition

**KPI:** Duplicate Rejection Rate

Formula:

Duplicate Rejection Rate = (Rejected Duplicate Attempts / Total Duplicate Attempts Tested) × 100

**Target:** 100%

**Verified Result:** 9 out of 9 explicitly documented duplicate-entry attempts were rejected.

**Calculation:** (9 / 9) × 100 = **100%**

**Status:** Target achieved for the documented test scenarios.

## 3. Supporting Test Evidence

The following test cases passed:

- **TC-02:** Duplicate employee ID rejected.
- **TC-03:** Duplicate email rejected.
- **TC-08:** Case-insensitive duplicate employee ID rejected.
- **TC-09:** Case-insensitive duplicate email rejected.
- **TC-11:** Duplicate email during employee update rejected.
- **TC-15:** Legacy database rejects a duplicate ID and a duplicate email (2 attempts).
- **TC-21:** Web application rejects a case-insensitive duplicate ID.
- **TC-22:** Web application rejects a case-insensitive duplicate email.
- **TC-28:** Web application rejects a duplicate email during update.

**Total duplicate attempts counted:** 9  
**Attempts rejected:** 9  
**Attempts accepted:** 0  
**Duplicate Rejection Rate:** 100%

Source: `../test-report.md`

## 4. TQM Interpretation

The results support the project's Poka-Yoke objective: preventing duplicate employee IDs and email addresses at database and application levels. The result applies to the explicitly documented test scenarios; it does not guarantee that every possible duplicate scenario has been tested.

## 5. Conclusion

All 9 documented duplicate-entry attempts were rejected, achieving the target Duplicate Rejection Rate of 100% for these tests. The automated test report provides supporting evidence for Quality Objective Q06.
