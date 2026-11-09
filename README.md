# School IT Help Desk

A Computer Science II project for reporting and managing school IT support
requests. Teachers and staff can submit tickets; users can view, search, filter,
assign, update, and resolve them. This is a classroom prototype and does not
include login accounts.

## Technology

- Python and Flask: web server, backend validation, business rules, and API
- SQLite: persistent ticket and technician data
- HTML and CSS: interface
- JavaScript and JSON: browser interactions and API communication
- Git and GitHub: version control and development history

## Architecture

The browser renders the interface and sends JSON requests to Flask. Flask
validates every request, applies ticket rules, and is the only component that
reads or writes SQLite. Flask returns a JSON result or a clear error for the
interface to display. The SQLite database must be stored on disk and survive
application restarts.

See [`docs/design.md`](docs/design.md) for the proposed schema, API, validation
rules, development phases, and acceptance tests.

## Project status

This repository is initialized for development. Application features and
automated tests have not yet been implemented or verified. See
[`docs/ai-review-log.md`](docs/ai-review-log.md) for the Phase 1 review status.

## Development and review workflow

- Work in approved, testable phases. Get the phase plan approved before
  implementation; do not build the whole application in one unapproved pass.
- At the end of each phase, review the changes and test evidence, update
  [`docs/ai-review-log.md`](docs/ai-review-log.md), then commit and push that
  phase's work. A commit is supporting history, not proof of authorship or
  correctness.
- Keep the AI development log accurate: capture approval decisions, errors,
  actual test commands and outputs, and corrections. Preserve relevant AI
  conversation evidence if requested.
- Be prepared to explain code, trace a request from browser through Flask to
  SQLite, reproduce an error, and make a small change during live teacher
  verification.
- Teacher review requires the code defense and tests; a finished-looking app
  does not replace the required workflow.

## Planned local setup

These are planned commands, not yet verified in this repository. Phase 1 must
add the Flask application and dependency file before the app can be run.

```powershell
python --version
git --version
python -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Once Phase 1 provides the Flask entry point and tests, its implementation
should document the exact application-start and test commands here.

## Data and privacy

Use fictional/sample data only. Do not commit the SQLite database or real
student, staff, or school information. The prototype is unauthenticated and is
not suitable for deployment on a public network.
