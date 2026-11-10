# Test Results

## Automated backend suite

**Date:** 2026-11-10
**Command (PowerShell, from the repository root):**

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

**Result:** `42 passed in 3.41s`

The suite uses a temporary SQLite database. It covers app startup and seeded
data, ticket creation and server-owned fields, input validation, room search
and combined filters, ticket details, technician assignment, status transitions,
resolution notes and timestamps, transaction rollback, persistence across app
recreation, and ordered ticket history including invalid and nonexistent IDs.

## Browser checks

On 2026-11-10, the browser was used to create ticket
`0beac375-05ed-49d6-b525-1501bbaa65f1`, move it from `Open` to `In Progress`
and then `Resolved`, and verify both transitions and their timestamps appeared
in the ticket history timeline. An Open sample ticket displayed the empty
history message.

Other browser results are recorded in
[`manual-test-matrix.md`](manual-test-matrix.md). These are implementation
checks, not Product Owner sign-off. Product Owner manual QA and the student's
live code defense remain pending as described in [`gates.md`](gates.md).
