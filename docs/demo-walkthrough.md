# Live Demo Walkthrough

This walkthrough was performed with the browser and local Flask server on
2026-11-10. It uses fictional data only.

## Start the application

From PowerShell:

```powershell
Set-Location -LiteralPath 'H:\AI vs AI\school-it-helpdesk'
& '.\.venv\Scripts\python.exe' app.py
```

Open <http://127.0.0.1:5000/>. Flask initializes the on-disk database and
displays the dashboard.

## Create, find, and update a ticket

1. Select **Submit a ticket** and enter:
   - Room: `Demo Room 88`
   - Device: `Demo projector`
   - Category: `Hardware`
   - Priority: `High`
   - Description: `The projector loses its signal during classroom presentations.`
2. Select **Create ticket**. The detail page shows its generated ID and `Open`
   status.
3. Go back to the dashboard. Search for `Demo Room 88`; the ticket appears.
   Open the ticket to display its details.
4. Assign **Jamie Chen** and save.
5. Select **In Progress** and save.
6. Select **Resolved**, enter
   `Replaced the HDMI cable and confirmed the projector signal is stable.`,
   and save. Verify the status, notes, and resolved timestamp on the details
   page.
7. On the dashboard, filter by room `Demo Room 88`, category `Hardware`,
   priority `High`, and status `Resolved`. The demo ticket is the matching row.

## Restart and verify persistence

Stop Flask with Ctrl+C in its terminal. Run the start command again, return to
the browser, and reload the dashboard. Apply the same filters and open the
ticket. Its resolved status, Jamie Chen assignment, resolution notes, and
resolved timestamp should remain.

## Observed demo run

- Ticket ID: `854f7ef7-ef21-4ca3-b94a-b77a32b7982b`
- Created `Demo Room 88` / `Demo projector`, category `Hardware`,
  priority `High`; the details page showed the generated ID and initial
  `Open` status.
- Assigned Jamie Chen and saved both transitions: `Open` -> `In Progress`
  -> `Resolved`. The database status history contained both transitions.
- Filtered by room `Demo Room 88`, category `Hardware`, priority `High`, and
  status `Resolved`: one matching row appeared.
- Stopped and restarted Flask, reloaded the dashboard, reapplied the filters,
  and reopened the same ticket. The filtered dashboard still showed one row;
  the detail page and SQLite record still showed:
  - Room: `Demo Room 88`; device: `Demo projector`
  - Status: `Resolved`; technician: `Jamie Chen`
  - Resolution notes: `Replaced the HDMI cable and confirmed the projector signal is stable.`
  - Resolution timestamp: `2026-11-10T18:56:44Z`

This is implementation-agent demo evidence, not the student's live code
defense or the Product Owner's independent QA. The Flask server is running at
<http://127.0.0.1:5000/> with this ticket's details page open.
