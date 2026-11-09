# Project Gates

The Product Owner approved these proposed gates on 2026-11-09. A gate is a
review checkpoint, not a claim that unperformed work has passed.

## Gate A — Requirements and plan approval

**Pass when:** The Product Owner approves phase scope, the 10 non-whitespace
character ticket-description minimum, and the project gate definitions before
implementation.

**Recorded outcome:** Approved in this chat on 2026-11-09. See
[`ai-review-log.md`](ai-review-log.md).

## Gate B — Implementation and automated verification

**Pass when:** The documented Flask/SQLite features are implemented; the
backend suite passes; persistent sample tickets, input rejection, search and
filters, assignment, transitions, resolution metadata, rollback, and restart
persistence are evidenced by tests; setup and commands work.

**Recorded outcome:** Passed on 2026-11-09. Flask startup and the dashboard
were observed in a browser; the backend suite passed 40 tests. See
[`ai-review-log.md`](ai-review-log.md) and
[`manual-test-matrix.md`](manual-test-matrix.md).

## Gate C — Product Owner manual QA and student code defense

**Pass when:** The Product Owner personally runs the documented manual test
matrix against the app and records observed results, and the student
independently completes the live explanation/error-reproduction/change
exercise described in `ai-review-log.md`.

**Recorded outcome:** Pending Product Owner QA and student live defense. The
implementation agent's browser checks are recorded, but do not count as the
Product Owner's independent QA.
