# ENTERPRISE-HRMS — INITIAL ARCHITECTURE AUDIT

## Audit Purpose

This audit compares the existing Enterprise-HRMS repository with the master architecture defined in `STRUCTURE.txt`.

The audit was performed before major new feature development to prevent duplication and unnecessary rebuilding.

---

# 1. APPLICATION INVENTORY

Existing applications include:

* accounts
* organization
* leave
* claims
* payroll
* recruitment
* performance
* training
* attendance_shifts
* assets
* documents
* compliance
* hrms_modules

---

# 2. RUNTIME VERIFICATION

## Django System Check

Result:

`System check identified no issues (0 silenced).`

## Tests

Result:

`Ran 3 tests`

`OK`

Current test coverage is very limited and must be expanded.

## Migration Check

Result:

`No changes detected`

## Migrations

Existing migrations are applied.

---

# 3. ARCHITECTURE FINDINGS

## Employee Profiles

Two models exist:

`accounts.EmployeeProfile`

`hrms_modules.EmployeeProfile`

Current data:

`accounts.EmployeeProfile = 0`

`hrms_modules.EmployeeProfile = 1`

The existing HRMS employee profile belongs to the admin user.

Conclusion:

DUPLICATED ARCHITECTURE.

Action:

Consolidate into one authoritative employee master record after dependency and migration analysis.

---

## Expense Claims

Two models exist:

`claims.ExpenseClaim`

`hrms_modules.ExpenseClaim`

Current data:

`claims.ExpenseClaim = 4`

`hrms_modules.ExpenseClaim = 0`

Conclusion:

DUPLICATED ARCHITECTURE.

The `claims` implementation is currently the authoritative data-bearing implementation.

Action:

Preserve existing claim records and consolidate API/workflow architecture.

---

## Leave

One primary model exists:

`leave.LeaveRequest`

However, multiple ViewSets/API surfaces expose the same domain.

Conclusion:

API duplication/fragmentation rather than database duplication.

Action:

Consolidate API architecture without deleting the underlying LeaveRequest model.

---

## Attendance

Attendance exists in:

`hrms_modules.Attendance`

Shift management exists separately in:

`attendance_shifts`

Conclusion:

These represent related but different domains.

Action:

Keep separate.

---

## Organization

Existing:

* Department
* Position

Conclusion:

Coherent foundation.

Action:

Extend existing organization architecture rather than creating another organization app.

---

## Documents

Existing:

`documents.EmployeeDocument`

Conclusion:

Model foundation exists.

Missing:

* complete document management workflow
* file handling
* versions
* expiry
* access control
* approval
* audit integration

Action:

Extend.

---

## Compliance / Audit

Existing:

`compliance.AuditLog`

Conclusion:

Model foundation exists.

Missing:

* automatic audit recording
* integration with important operations
* complete change history

Action:

Extend into reusable audit infrastructure.

---

## Payroll

Existing:

* EmployeeSalary
* Payslip

Conclusion:

Model foundation only.

Missing:

* payroll engine
* periods
* processing
* allowances
* deductions
* tax
* pension
* approvals
* reports
* audit

Action:

Extend existing payroll application.

---

## Recruitment

Existing:

* JobVacancy
* Applicant

Conclusion:

Foundation exists.

Missing:

* requisitions
* approvals
* screening
* shortlisting
* interviews
* assessments
* offers
* background checks
* hiring workflow

Action:

Extend existing recruitment application.

---

## Performance

Existing:

* PerformanceGoal
* Appraisal
* API
* Employee 360 integration

Conclusion:

Functional foundation exists.

Action:

Extend rather than rebuild.

---

## Training

Existing:

* TrainingCourse
* EmployeeCertification
* API
* Employee portal integration

Conclusion:

Functional foundation exists.

Action:

Extend rather than rebuild.

---

## Assets

Existing:

* CompanyAsset
* categories
* assigned employee
* serializer
* ViewSet
* API
* admin
* employee portal
* Employee 360 integration

Conclusion:

Functional foundation exists.

Action:

Extend rather than rebuild.

---

# 4. SECURITY FINDINGS

Current User roles:

* ADMIN
* MANAGER
* EMPLOYEE

Problem:

The role field exists but comprehensive role-to-permission enforcement is not established.

Additional findings:

* Claims uses AllowAny
* Leave uses AllowAny
* Approval endpoints lack demonstrated role-specific authorization
* Employee profile API is more permissive than an enterprise HR system should be

Action:

Build centralized RBAC and permission enforcement.

---

# 5. KNOWN CODE DEFECT

`accounts.UserSerializer.update()` contains a suspected indentation/logic defect in profile update handling.

This has not been sufficiently covered by existing tests.

Action:

Create a regression test before/while fixing it.

---

# 6. FRONTEND/API DEPENDENCIES

Existing frontend pages depend on APIs including:

* `/api/claims/`
* `/api/leave/`
* `/api/attendance/`
* `/api/attendance/check_out/`
* `/api/employee-360/<userId>/`

Therefore:

API consolidation must preserve or deliberately migrate frontend consumers.

Do not delete existing endpoints blindly.

---

# 7. TESTING FINDINGS

Current test suite contains only a small number of tests.

Required future coverage:

* authentication
* permissions
* employee creation
* employee update
* employee profile consolidation
* Employee 360
* organization
* documents
* attendance
* leave
* claims
* payroll
* recruitment
* performance
* training
* assets
* workflows
* audit

---

# 8. CURRENT ARCHITECTURAL PRIORITY

Priority 1:

Single authoritative Employee Master Record.

Priority 2:

Role + Permission architecture.

Priority 3:

Reusable Audit infrastructure.

Priority 4:

Complete V1 Core HR.

Priority 5:

V2 Workforce.

Priority 6:

V3 Talent.

Priority 7:

V4 Finance.

Priority 8:

V5 Enterprise.

---

# 9. IMPORTANT CONCLUSION

The repository is not an empty project.

It already contains substantial functionality.

Therefore development must follow a consolidation-and-extension strategy rather than a rebuild strategy.

The objective is:

`EXISTING SYSTEM + REQUIRED GAPS = COMPLETE ENTERPRISE-HRMS`

not:

`EXISTING SYSTEM → DELETE → REBUILD`

---

# 10. AUDIT STATUS

Initial architecture audit:

COMPLETE

Master requirements:

DOCUMENTED

Development control rules:

DOCUMENTED

Next implementation task:

V1.01 — Employee Master Architecture
