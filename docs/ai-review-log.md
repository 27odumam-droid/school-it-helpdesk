# AI Review Log

This log records phase scope, review decisions, implementation evidence, and
Product Owner QA. An AI statement that a feature works is not evidence; record
commands, observed results, and manual checks.

For every phase, record approval decisions, errors, corrections, exact test
commands and their observed outputs, and relevant AI conversation references
when available. Do not invent or summarize test output as if it were observed.
At the end of an approved phase, review its changes and evidence, then record
the commit and push references. Commits document history but do not by
themselves establish authorship or correctness.

### Phase record template

Copy this template for each new phase:

```text
## Phase N — [name]

Status:
Approved scope and decisions:
Implementation summary:
Errors encountered and corrections:
Tests (exact commands and observed output):
Manual QA:
AI conversation evidence/reference:
Commit:
Push:
Readiness decision:
```

Teacher live verification may ask the student to explain a function, trace a
request from browser through Flask to SQLite, reproduce an error, or make a
small change. Record the student's verification notes when performed. A phase
or application is not ready for teacher review solely because it looks
complete; implementation must follow the approved workflow and pass code
defense and tests.

## Phase 1 — Foundation and persistent database

**Status:** Proposed design prepared; implementation not started or verified.

**Scope for this phase**

- Inspect the repository and confirm the Python/Flask project structure.
- Create a minimal Flask application and document setup/run/test commands.
- Initialize a persistent, on-disk SQLite database.
- Define the initial schema for tickets, fictional technicians, and ticket
  status history, including constraints and foreign keys.
- Seed a stable fictional technician list without duplicating entries on
  repeated initialization.
- Document database location and safe development reset procedure.

**Out of scope:** Ticket form, dashboard, search/filter UI, ticket CRUD API,
assignment UI, status transition behavior, authentication, and deployment.

**Design review**

- Frontend-to-backend-to-database architecture and proposed schema are recorded
  in [`design.md`](design.md).
- Keep SQLite out of static/public assets; enable foreign keys.
- Use only fictional/sample data and do not commit the database.
- The description minimum remains a Product Owner decision; recommendation is
  10 non-whitespace characters. It is not a Phase 1 implementation requirement.

**Implementation evidence:** Pending. No code, setup, database initialization,
or tests have been reviewed for this phase.

**Product Owner QA:** Pending.

**Readiness decision:** Not ready for teacher review. Reassess after an approved
implementation, observed test results, and Product Owner QA.

**Evidence to attach when implementation is returned**

- Changed-file summary and exact setup/run/test commands.
- Actual test output for database initialization, schema constraints, foreign
  keys, technician seeding/idempotence, and persistence across app restart.
- Manual Product Owner check that the documented database path is correct and
  sample data survives restarting the application.
