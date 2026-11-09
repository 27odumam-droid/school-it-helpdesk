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
- No approval to claim Product Owner QA or the student's live code defense;
  those require the actual participants and remain pending until performed.

## Phase 1 — Flask foundation and persistent database

**Status at approval:** Approved; implementation pending.

**Approved scope:** Flask app factory, on-disk SQLite schema, foreign-key
enforcement, idempotent fictional technician and sample-ticket seed data,
start/setup instructions, and focused database tests.

**Implementation evidence:** To be recorded after implementation.
**Tests (exact command and observed output):** Pending.
**Manual QA:** Pending.

**Commit:** Pending.
**Push:** Pending.
**Readiness decision:** Pending test evidence and Product Owner review.

## Phase 2 — Ticket creation, validation, and dashboard

**Status at approval:** Approved; implementation pending.

**Approved scope:** Public submission; server validation and generated ticket
fields; dashboard, ticket details, room search, and combined filters.

**Implementation evidence:** To be recorded after implementation.
**Tests (exact command and observed output):** Pending.
**Manual QA:** Pending.

**Commit:** Pending.
**Push:** Pending.
**Readiness decision:** Pending test evidence and Product Owner review.

## Phase 3 — Assignment, status workflow, and integration

**Status at approval:** Approved; implementation pending.

**Approved scope:** Persisted fictional technician assignment; allowed status
transitions; mandatory resolution notes; atomic resolution metadata and status
history; restart persistence; complete test matrix and gates.

**Implementation evidence:** To be recorded after implementation.
**Tests (exact command and observed output):** Pending.
**Manual QA:** Pending.

**Commit:** Pending.
**Push:** Pending.
**Readiness decision at approval:** Not ready for teacher review until
implementation, automated tests, manual QA, and the student's live code
defense are completed.

## Student live verification

**Status:** Not performed.

The student should explain `create_app`, trace a submission from the form
through Flask validation into SQLite, explain how the status transaction rolls
back when history recording fails, reproduce a rejected request, and make a
small live code change. Record the student's actual demonstration and
teacher/owner feedback here only after it happens.
