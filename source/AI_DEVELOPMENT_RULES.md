# ENTERPRISE-HRMS — AI DEVELOPMENT RULES

## 1. PURPOSE

This document controls how AI assistants and developers must work on the Enterprise-HRMS project.

The master source of truth for the system structure is:

`STRUCTURE.txt`

The AI must use the existing repository as the source of truth for what has already been implemented.

The AI must not repeatedly rebuild features that already exist.

---

# 2. MASTER DEVELOPMENT PRINCIPLE

The AI must follow this cycle for every requirement:

1. Read the requirement.
2. Inspect the existing repository.
3. Identify existing implementations.
4. Trace dependencies.
5. Compare the implementation with the requirement.
6. Classify the requirement.
7. Implement only the missing or defective parts.
8. Run tests and system checks.
9. Verify that existing functionality still works.
10. Update PROJECT_PROGRESS.md.
11. Move to the next unfinished requirement.

The required cycle is:

`INSPECT → COMPARE → PLAN → IMPLEMENT → TEST → VERIFY → RECORD → CONTINUE`

---

# 3. NEVER REBUILD WITHOUT EVIDENCE

The AI must never create a new model, application, API, serializer, view, template, or service merely because a requirement exists.

Before implementing anything, search the repository.

The AI must determine whether the requirement is:

* COMPLETE
* PARTIAL
* MISSING
* BROKEN
* DUPLICATED
* BLOCKED

---

# 4. DUPLICATE DETECTION

Before creating a new feature, search for:

* model names
* database tables
* serializers
* ViewSets
* function-based views
* URLs
* templates
* JavaScript endpoints
* admin registrations
* migrations
* services
* tests

If duplicate functionality exists, do not automatically delete either implementation.

First determine:

1. Which implementation contains real data?
2. Which implementation is actively used?
3. Which implementation is referenced by URLs?
4. Which implementation is referenced by templates?
5. Which implementation is referenced by JavaScript?
6. Which implementation has the better domain model?
7. What data must be preserved?
8. What dependencies must be migrated?

Only after this analysis may consolidation occur.

---

# 5. DATA PRESERVATION

Existing database data must never be deleted merely to simplify development.

Before changing or removing a model:

* inspect record counts
* inspect existing records
* inspect foreign-key relationships
* inspect migrations
* identify dependent code
* create a migration strategy
* preserve existing information

Database changes must be reversible or safely migrated wherever practical.

---

# 6. MASTER EMPLOYEE PRINCIPLE

Enterprise-HRMS must maintain one authoritative employee master record.

The system must avoid creating multiple independent employee profile models representing the same employee.

Employee 360 should integrate information from the authoritative employee record and related modules.

---

# 7. DO NOT BREAK EXISTING MODULES

Before changing a shared model or API, identify dependent modules.

Examples include:

* organization
* leave
* claims
* payroll
* performance
* training
* assets
* documents
* attendance
* Employee 360
* dashboards

After shared architecture changes, run the relevant tests and system checks.

---

# 8. API RULES

Before creating an API endpoint:

1. Search for an existing endpoint serving the same purpose.
2. Check URL routing.
3. Check ViewSets.
4. Check serializers.
5. Check frontend JavaScript.
6. Check templates.
7. Check permissions.

Existing frontend endpoints must not be removed without updating their consumers.

---

# 9. SECURITY RULES

Authentication is not the same as authorization.

The AI must verify:

* authentication
* role
* permission
* object ownership
* approval authority
* sensitive-data access

Approval, payroll, employee-management, document-management, and administrative operations must not rely only on generic authentication.

Do not use `AllowAny` for sensitive HR operations unless the requirement explicitly requires public access.

---

# 10. ROLE AND PERMISSION ARCHITECTURE

Do not hard-code business authorization around only:

* `is_superuser`
* `is_staff`
* username
* individual conditionals scattered throughout views

The target architecture is a configurable Role + Permission system.

The master structure defines roles including:

* SUPER ADMIN
* SYSTEM ADMIN
* HR ADMIN
* HR OFFICER
* RECRUITMENT OFFICER
* PAYROLL OFFICER
* FINANCE OFFICER
* TRAINING OFFICER
* MANAGER
* EMPLOYEE
* EXECUTIVE
* AUDITOR

These must eventually be implemented through permissions rather than hard-coded assumptions.

---

# 11. WORKFLOW RULES

Approval processes must be treated as business workflows.

Examples:

Leave:

Employee → Manager → HR → Approved

Salary Change:

Manager → HR → Finance → Executive → Approved

The AI must not implement approval logic independently in many unrelated views if the requirement calls for a reusable workflow engine.

---

# 12. TESTING RULES

Every significant implementation must have tests.

At minimum, test:

* model behavior
* serializer behavior
* API behavior
* permissions
* workflow transitions
* invalid input
* existing-data preservation
* important user roles

Before marking a task COMPLETE:

`python manage.py check`

must pass.

The relevant test suite must pass.

Where appropriate:

`python manage.py makemigrations --check`

must also pass.

---

# 13. REGRESSION PROTECTION

If a bug is discovered in existing functionality:

1. Reproduce it.
2. Add a regression test where practical.
3. Fix the implementation.
4. Run the regression test.
5. Run the wider relevant test suite.
6. Record the fix in PROJECT_PROGRESS.md.

---

# 14. MIGRATION RULES

Never manually delete migrations simply because the migration history looks complicated.

Before migration changes:

* inspect current migrations
* inspect database state
* run `showmigrations`
* run `makemigrations --check`

After model changes:

* generate appropriate migration
* inspect migration
* apply migration
* verify data

---

# 15. UI RULES

Do not rebuild existing pages without checking whether they are already used.

Before replacing a dashboard or page:

* identify its URL
* identify its templates
* identify API calls
* identify JavaScript dependencies
* identify users who depend on it

The target UI should be enterprise-grade, consistent, responsive, and maintainable.

---

# 16. REQUIREMENT STATUS DEFINITIONS

COMPLETE:
The requirement is implemented and verified by appropriate tests/evidence.

PARTIAL:
Some required functionality exists but important requirements remain.

MISSING:
No meaningful implementation exists.

BROKEN:
Implementation exists but does not correctly perform the requirement.

DUPLICATED:
Multiple implementations represent the same business capability.

BLOCKED:
Implementation should not proceed because an architectural or dependency decision must be resolved first.

---

# 17. TASK COMPLETION RULE

A task may only be marked COMPLETE after:

* implementation exists
* dependencies are verified
* tests pass
* system checks pass
* migrations are valid
* no known regression has been introduced
* PROJECT_PROGRESS.md has been updated

---

# 18. NEVER SKIP THE GAP ANALYSIS

For every requirement, the AI must answer:

### Requirement

What exactly does the master structure require?

### Existing implementation

What already exists?

### Evidence

Which files, models, APIs, templates, migrations, or tests prove it?

### Gap

What is missing?

### Dependencies

What existing functionality could be affected?

### Action

What exactly should be changed?

### Verification

How will completion be tested?

---

# 19. DEVELOPMENT ORDER

Follow the master roadmap:

V1 — CORE HR

V2 — WORKFORCE

V3 — TALENT

V4 — FINANCE

V5 — ENTERPRISE

Do not jump to advanced modules merely because they are interesting.

However, dependencies may require architectural preparation before a later module is implemented.

---

# 20. CURRENT PROJECT PRIORITY

The first major architectural priority is establishing a single authoritative Employee Master Record.

Current known duplicate:

`accounts.EmployeeProfile`

and

`hrms_modules.EmployeeProfile`

The AI must preserve existing employee data before consolidation.

After employee architecture:

1. RBAC and permissions
2. Audit infrastructure
3. V1 Employee features
4. Organization expansion
5. Documents
6. Employee 360
7. V2 Workforce
8. V3 Talent
9. V4 Finance
10. V5 Enterprise

---

# 21. FINAL AI RULE

NEVER ASSUME.

INSPECT THE CODE.

NEVER REBUILD BLINDLY.

COMPARE WITH WHAT EXISTS.

NEVER DELETE DATA TO MAKE DEVELOPMENT EASIER.

PRESERVE EXISTING FUNCTIONALITY.

NEVER MARK A FEATURE COMPLETE WITHOUT VERIFICATION.

UPDATE PROJECT_PROGRESS.md AFTER EVERY SIGNIFICANT TASK.

THEN MOVE TO THE NEXT UNFINISHED REQUIREMENT.

The goal is not to continuously generate code.

The goal is to systematically transform the existing repository into the complete Enterprise-HRMS defined by STRUCTURE.txt.
