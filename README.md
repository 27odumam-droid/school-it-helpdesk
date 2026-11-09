# School IT Help Desk

A classroom prototype for submitting and managing fictional school IT support
requests. It uses Python, Flask, SQLite, HTML, CSS, and JavaScript. No login is
required; do not use real student or staff data or expose the app to a public
network.

## Features

- Public ticket submission with server-side validation and server-generated
  UUID, UTC timestamps, and initial `Open` status.
- Dashboard with room search and combined category, priority, and status
  filters; complete ticket details.
- Fictional technician assignment and the `Open` → `In Progress` → `Resolved`
  workflow. Resolution requires notes and is saved atomically with status
  history and a resolution timestamp.
- Persistent SQLite storage, five fictional technicians, and 15 repeatable
  fictional sample tickets.

## Requirements and setup

Install Python 3.10 or later and ensure its executable is available in
PowerShell (add it to `PATH` or use the Python Launcher). From the repository
root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the `python` command opens the Microsoft Store instead of Python, disable
the Windows Python app execution alias or run the installed `python.exe` by
its full path for the virtual-environment creation step.

`requirements.txt` contains Flask and pytest. SQLite is included with Python;
no separate database server is needed.

## Run and test

```powershell
.\.venv\Scripts\python.exe app.py
```

Open <http://127.0.0.1:5000/>. Flask initializes the database and fictional
seed data on startup. To run the backend test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite uses a temporary SQLite database, not the development database.
Run Flask locally only; the unauthenticated dashboard and update endpoints
must not be deployed publicly.

## Database and reset

The default on-disk database is `instance/helpdesk.sqlite3`, outside Flask's
public static directory and ignored by Git. The app creates its parent
directory, schema, technicians, and stable sample tickets on startup. Seed
inserts are idempotent and do not overwrite existing tickets.

To intentionally reset local development data, stop the app, make a backup if
needed, and remove only `instance/helpdesk.sqlite3` (and its SQLite journal
files if present). The next start creates a fresh database. Never commit the
database or store real school data in it.

## Architecture

The browser renders Jinja templates and uses same-origin JSON requests in
`static/app.js`. `helpdesk/routes.py` validates input and applies workflow
rules; `helpdesk/db.py` initializes and accesses SQLite. Resolution and status
history writes share a transaction. See [`docs/design.md`](docs/design.md) for
the schema, API, and acceptance criteria.

## Project review and classroom gates

- [docs/ai-review-log.md](docs/ai-review-log.md) records approved scope,
  implementation evidence, review decisions, and commit hashes.
- [docs/manual-test-matrix.md](docs/manual-test-matrix.md) records observed
  manual UI checks and their results.
- [docs/gates.md](docs/gates.md) defines Gates A, B, and C.
- [docs/code-defense-guide.md](docs/code-defense-guide.md) prepares the
  student for the required live explanation and coding exercise.

Gate C requires the Product Owner's manual QA and the student's own live code
defense. An AI implementation cannot claim to have completed that defense.
Use [docs/phase-1-work-order.md](docs/phase-1-work-order.md) as the approved
implementation handoff.
