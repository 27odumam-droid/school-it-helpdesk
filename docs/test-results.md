# Test Results

**Test date:** 2026-11-12

**Test data:** Temporary SQLite database; the development database was not changed.

## Summary

- **Automated backend tests:** PASS — 43 passed in 4.89 seconds.
- **Browser checks:** PASS — dashboard, ticket creation, validation, search,
  assignment, status updates, resolution, and refresh were checked in the UI.
- **App restart persistence:** PASS — a fictional ticket and its assignment,
  resolved status, notes, timestamp, and status history remained after Flask
  was stopped and restarted with the same SQLite database.
- **Features not built yet:** None identified in the requested checklist.

## Test results

### App and ticket creation

| # | What was tested | What should happen | What actually happened | Result |
|---|---|---|---|---|
| 1 | Open the app dashboard. | The app loads without errors. | Dashboard and supporting APIs returned successfully, 15 fictional sample tickets loaded, and the browser reported no JavaScript page errors. | **PASS** |
| 2 | Submit a valid new ticket. | The ticket is saved and its details are available. | A ticket was created with HTTP 201 and opened on its details page with an ID and `Open` status. | **PASS** |
| 3 | Leave a required field blank. | Submission is blocked and an error is indicated. | Browser validation marked the required controls invalid and kept the form open; backend tests also confirmed missing required fields return HTTP 400. | **PASS** |
| 4 | Create two tickets. | Each ticket receives a different ID. | Created `a1edc5f0-cd2c-4143-b886-df6a30a7f835` and `4b848ca5-d386-4c3e-b548-31c6e03de542`; the IDs differ. | **PASS** |

### Viewing and managing tickets

| # | What was tested | What should happen | What actually happened | Result |
|---|---|---|---|---|
| 5 | View the tickets dashboard. | Saved tickets appear in the list. | Dashboard listed 17 tickets (15 samples plus both newly created tickets). | **PASS** |
| 6 | Search for a ticket. | Search results match the selected criteria. | `QA Room Alpha` and `QA Room Beta` searches each returned exactly their matching ticket with the selected category, priority, and status. | **PASS** |
| 7 | Change ticket status. | The selected status is saved. | The Alpha ticket moved from `Open` to `In Progress` to `Resolved`; both transitions appeared in its history after reload. | **PASS** |
| 8 | Assign a technician. | The technician assignment is saved. | Alex Rivera was assigned to the Alpha ticket and remained selected in the dashboard and details after refresh. | **PASS** |
| 9 | Resolve a ticket. | Resolution notes and resolved status are saved. | Blank resolution notes were blocked by required-field validation. With notes supplied, the ticket showed `Resolved`, the saved notes, and a resolution timestamp. | **PASS** |

### Persistence

| # | What was tested | What should happen | What actually happened | Result |
|---|---|---|---|---|
| 10 | Refresh the ticket page. | Saved ticket data remains visible. | After reloading details, resolved status, Alex Rivera, resolution notes, timestamp, and status history remained present. | **PASS** |
| 11 | Stop and restart Flask using the same database. | Saved data remains available after startup. | Created fictional ticket `c5cf5b99-c217-47f6-ba47-a3ceb4bb6680`, assigned Jamie Chen, moved it through `In Progress` to `Resolved`, and saved notes. Stopped Flask, restarted it with the same SQLite file, then reopened the ticket. Resolved status, Jamie Chen assignment, resolution notes, resolved timestamp (`2026-11-12 1:05:02 PM` local display), and both status-history entries remained. | **PASS** |

## Test execution notes

The repository-local `pytest.ini` sets the test directory and confines
`conftest.py` discovery to `tests`, avoiding parent-workspace configuration.
The documented command was run from the repository root:

```powershell
Set-Location -LiteralPath 'H:\AI vs AI\school-it-helpdesk'; & '.\.venv\Scripts\python.exe' -m pytest -c pytest.ini -q
```

Exact output:

```text
...........................................                              [100%]
43 passed in 4.89s
```

For the live restart check, Flask was started with
`HELPDESK_DATABASE` set to the temporary file
`%TEMP%\helpdesk-restart-verification.sqlite3`. After the ticket changes were
saved, Flask was stopped and started again with the same environment variable
and database path; the ticket details page was reloaded and all persisted
values were checked.

These are implementation checks, not Product Owner sign-off. The browser
matrix is also recorded in [`manual-test-matrix.md`](manual-test-matrix.md).
Product Owner QA and the student's live code defense remain pending as
described in [`gates.md`](gates.md).
