# AI Review Log

Record phase approvals, decisions, errors, corrections, exact test commands
and observed output, QA, and commit/push references. Do not invent evidence:
a commit records history, not authorship or correctness.

## Approval and decisions — 2026-11-09

- Product Owner approved completing the full application checklist and the
  phase-based plan in this repository.
- Approved the design's recommendation of at least 10 non-whitespace
  characters for ticket descriptions. Resolution notes are required to be
  non-empty, without an additional minimum.
- Approved the proposed gate definitions in [`gates.md`](gates.md).
- Gate A passed. The plan approval commit is
  `0a47687526caf96fd5a372537fb8acb9b7420137`.
- Product Owner manual QA and student live code defense remain pending until
  performed by those participants.

## Phase 1 — Flask foundation and persistent database

**Status:** Implemented and verified; Product Owner QA pending.

**Approved scope:** Flask app, persistent on-disk SQLite schema, per-connection
foreign-key enforcement, idempotent technician and 15-ticket fictional seed
data, setup/run instructions, database constraints, and persistence tests.

**Implementation:** `app.py`; `helpdesk/__init__.py`; `helpdesk/db.py`;
`requirements.txt`; and database cases in `tests/test_app.py`.

**Errors and corrections:** Python was initially unavailable. Python 3.12.10
was installed in the current Windows user scope; Flask and pytest were
installed in the ignored project `.venv`. The first pytest invocation used an
absolute test-file path while the shell was in the parent directory and failed
with `ModuleNotFoundError: No module named 'helpdesk'`. Running pytest from the
repository root fixed test discovery.

**Tests (exact command and observed output):**

```powershell
Set-Location -LiteralPath 'H:\AI vs AI\school-it-helpdesk'; & '.\.venv\Scripts\python.exe' -m pytest -q
```

Final output: `40 passed in 3.63s`.

**Manual startup evidence:** Ran `.venv\Scripts\python.exe app.py`; the
dashboard and API returned HTTP 200. Startup seeded 15 tickets and 5
technicians. After the browser-created test ticket, the on-disk database
contained 16 tickets and 5 technicians.

**Product Owner QA:** Pending.
**Implementation commit:** Pending.
**Push:** Not pushed; awaiting review.
**Readiness decision:** Gate B passed; Gate C pending.

## Phase 2 — Ticket creation, validation, and dashboard

**Status:** Implemented and verified; Product Owner QA pending.

**Approved scope:** Public ticket submission, authoritative server validation,
server-generated UUID and timestamps, initial `Open` status, dashboard,
details, room search, and combined category/priority/status filters.

**Implementation:** `helpdesk/validation.py`, ticket and page routes,
templates, browser JavaScript/CSS, and backend validation/API tests.

**Errors and corrections:** The first application test exposed
`TemplateNotFound: dashboard.html` because Flask's package root differed from
the repository-level `templates` directory. Configured the app to resolve the
repository-level `templates` and `static` folders.

**Tests:** The same exact pytest command above; final output
`40 passed in 3.63s`.

**Browser results:** Created ticket
`d46a1418-f485-45b6-aa2b-21990d36b3de`; the details page showed its room,
creation time, and `Open` status. A whitespace-only room submission returned
`400` with “Room is required.” Room `101` plus Hardware/Low/Open filters
returned one matching ticket. More UI results are recorded in
[`manual-test-matrix.md`](manual-test-matrix.md).

**Product Owner QA:** Pending.
**Implementation commit:** Pending.
**Push:** Not pushed; awaiting review.
**Readiness decision:** Gate B passed; Gate C pending.

## Phase 3 — Assignment, status workflow, and integration

**Status:** Implemented and verified; Product Owner QA and student defense
pending.

**Approved scope:** Validated technician assignment; `Open` -> `In Progress`
-> `Resolved`; mandatory resolution notes; atomic ticket/history update;
resolution timestamp; failure handling; browser refresh and app restart
persistence; and project gate/review documentation.

**Implementation:** Assignment and status API/UI, transaction and failure
tests, setup/manual-test documentation, gates, and
[`code-defense-guide.md`](code-defense-guide.md).

**Errors and corrections:** Browser testing revealed that a hidden
resolution-notes textarea marked `required` prevented the `Open` ->
`In Progress` update. The UI now requires the field only when `Resolved` is
selected; server-side validation remains authoritative.

**Tests:** The same exact pytest command above; final output
`40 passed in 3.63s`. Tests include invalid-input rejection, status transitions,
resolution-note validation, a forced status-history write failure with
rollback, database write failure, and data surviving app recreation.

**Browser restart evidence:** Assigned Alex Rivera, advanced the ticket
through both permitted statuses, rejected whitespace-only resolution notes,
then saved valid notes and a resolution timestamp. After browser refresh and
Flask restart, the details page and filtered dashboard retained resolved
status, assignment, notes, and timestamp. See
[`manual-test-matrix.md`](manual-test-matrix.md).

**Product Owner QA:** Pending; implementation-agent browser results are not
Product Owner sign-off.
**Student live defense:** Not performed.
**Implementation commit:** Pending.
**Push:** Not pushed; awaiting review.
**Readiness decision:** Gate B passed. Not ready for teacher review until
Gate C's Product Owner QA and student defense are completed.

## Student live verification

**Status:** Not performed.

Use [`code-defense-guide.md`](code-defense-guide.md). The student should
explain `create_app`, trace a request from browser through Flask to SQLite,
explain the atomic status/history update and rollback test, reproduce a
rejected request, and make a small live code change. Record the student's
actual demonstration and teacher/owner feedback here only after it happens.
