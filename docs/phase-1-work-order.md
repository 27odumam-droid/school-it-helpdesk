# VS Code AI Work Order — Approved Implementation

You are the Junior Developer for the School IT Help Desk project. Read
`README.md`, `docs/design.md`, and `docs/ai-review-log.md` before starting.

## Approval

The Product Owner approved the full checklist and phase-based implementation
plan on 2026-11-09, including the 10 non-whitespace character minimum for
ticket descriptions and the proposed gates documented in `gates.md`. The
plan-first stop condition has been satisfied. Implement and verify the phases
below; report only evidence actually observed.

## Approved scope

1. Implement a Flask app and setup/run/test instructions.
2. Initialize persistent SQLite schema, enable foreign keys, and seed stable
   fictional technicians idempotently.
3. Generate at least 15 deterministic fictional tickets without overwriting
   user-created data.
4. Implement public ticket submission, server-side validation, unique
   server-generated ID, creation/update timestamps, and initial `Open` status.
5. Implement a dashboard, details view, room search, and combined category,
   priority, and status filters.
6. Persist assignment from validated fictional technicians.
7. Support only `Open` -> `In Progress` -> `Resolved`. Require non-empty
   resolution notes and atomically persist status history, notes, resolution
   timestamp, and the existing assignment.
8. Add automated backend coverage for database constraints/initialization,
   validation, IDs, search/filters, assignment, status workflow, atomic
   rollback, database errors, and restart persistence.
9. Update the README, actual manual test matrix, phase review log, and gate
   documentation.

Do not add sign-in or authorization. Use fictional data only and do not deploy
the unauthenticated prototype publicly.

## Evidence and handoff

For each phase, record exact changed files, commands and observed results,
errors/corrections, actual manual QA, and the phase commit hash in
`docs/ai-review-log.md`. Do not mark Product Owner QA or student defense
complete unless they actually occurred. Do not claim readiness for teacher
review while either remains pending. Push only after authorized review and
when the repository remote is available.
