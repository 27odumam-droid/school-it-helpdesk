# Student Code Defense Guide

The student must perform the live defense personally; this guide is for
preparation, not proof that the defense happened. The app is an unauthenticated
classroom prototype. Use fictional data only.

## Explain and trace

1. In `helpdesk/__init__.py`, explain what `create_app` configures and why
   database initialization runs when the app is created.
2. Trace a form submission through `static/app.js`,
   `helpdesk/routes.py`, `helpdesk/validation.py`, and `helpdesk/db.py`.
   Identify which ticket fields are controlled by the server.
3. Explain how parameterized SQL and UUID validation are used.
4. Explain the `Open` -> `In Progress` -> `Resolved` transition rules and why
   resolution notes and status history are saved in one transaction.
5. Explain what happens when SQLite rejects a write and which test proves
   partial resolution changes are rolled back.
6. Describe how to run the test suite and where persistent SQLite data lives.

## Live exercise

With the teacher, choose one small fictional-data change (for example, change
the dashboard's empty-state message), implement it live, and run the relevant
check. Then reproduce a rejected server-side input and explain why it was
rejected.

Record the date, student's explanations, live change, commands/results, and
teacher feedback in `docs/ai-review-log.md` after the exercise. Until then,
Gate C and the live-defense checklist item remain incomplete.
