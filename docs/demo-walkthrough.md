# Live Demo Walkthrough

This walkthrough was performed with the browser and local Flask server on
2026-11-09. It uses fictional data only.

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
   - Room: `Demo Room 77`
   - Device: `Demo projector`
   - Category: `Hardware`
   - Priority: `High`
   - Description: `The projector loses its signal during classroom presentations.`
2. Select **Create ticket**. The detail page shows its generated ID and `Open`
   status.
3. Go back to the dashboard. Search for `Demo Room 77`; the ticket appears.
   Open the ticket to display its details.
4. Assign **Jamie Chen** and save.
5. Select **In Progress** and save.
6. Select **Resolved**, enter
   `Replaced the HDMI cable and confirmed the projector signal is stable.`,
   and save. Verify the status, notes, and resolved timestamp on the details
   page.
7. On the dashboard, filter by room `Demo Room 77`, category `Hardware`,
   priority `High`, and status `Resolved`. The demo ticket is the matching row.

## Restart and verify persistence

Stop Flask with Ctrl+C in its terminal. Run the start command again, return to
the browser, and reload the dashboard. Apply the same filters and open the
ticket. Its resolved status, Jamie Chen assignment, resolution notes, and
resolved timestamp should remain.

## Observed demo run

- Ticket ID: `2ae99622-4777-48ae-9a13-dd08810d1978`
- Filtered dashboard: one matching resolved ticket.
- After Flask restart, the detail page and API still showed:
  - Room: `Demo Room 77`; device: `Demo projector`
  - Status: `Resolved`; technician: `Jamie Chen`
  - Resolution notes: `Replaced the HDMI cable and confirmed the projector signal is stable.`
  - Resolution timestamp: `2026-11-09T19:23:54Z`

This is implementation-agent demo evidence, not the student's live code
defense or the Product Owner's independent QA.
