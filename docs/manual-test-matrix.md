# Manual Test Matrix

Run these checks in a browser against a local app started with the README
command. The results below were observed in the implementation agent's browser
session on 2026-11-09; this evidence does not substitute for the Product
Owner's own QA. Do not enter real student or staff data.

| # | Action | Expected result | Actual result |
|---|---|---|---|
| 1 | Start Flask and open the dashboard. | Dashboard loads and shows at least 15 fictional tickets. | **Pass:** Flask returned the dashboard; browser showed “15 tickets found”; API returned 15 tickets and 5 fictional technicians. |
| 2 | Submit a ticket with all valid fields. | Details page shows a new ID, creation time, and `Open` status. | **Pass:** Created `d46a1418-f485-45b6-aa2b-21990d36b3de`; details showed room, UTC creation time, and `Open`. |
| 3 | Submit a ticket with blank required fields or a too-short description. | Form/backend displays an error; no ticket is added. | **Pass:** Whitespace-only room was rejected with “Room is required.”; no ticket was created. |
| 4 | Search by a room that appears in sample data. | Matching room tickets appear; unrelated rooms do not. | **Pass:** Room `101` plus Hardware/Low/Open filters returned only the matching ticket. |
| 5 | Combine room, category, priority, and status filters. | Every visible ticket matches all selected criteria. | **Pass:** Combined query displayed one matching `101` / Hardware / Low / Open ticket. |
| 6 | Open a ticket and assign a fictional technician. | Assignment appears in details and dashboard after refresh. | **Pass:** Assigned Alex Rivera; after app restart, details and the room-filtered dashboard both showed the assignment. |
| 7 | Change a ticket from `Open` through `In Progress` to `Resolved`; refresh after updates. | Permitted status changes are saved. | **Pass:** UI saved `In Progress`, then `Resolved`; resolved status remained after browser refresh and app restart. |
| 8 | Attempt to resolve without notes, then add notes and resolve. | First attempt is rejected; second saves notes and a resolution time. | **Pass:** Whitespace-only notes returned “Resolution notes is required.” and left status unchanged; valid notes resolved the ticket and displayed `resolved_at`. |
| 9 | Refresh after creation/updates and restart Flask. | Saved ticket and changes remain available. | **Pass:** Browser refresh and Flask restart retained resolved status, Alex Rivera assignment, notes, and resolution timestamp. |
| 10 | Open a ticket with status changes and inspect its history. | Recorded transitions appear in order with timestamps; a ticket without transitions has a clear empty state. | **Pass (2026-11-10):** Created `0beac375-05ed-49d6-b525-1501bbaa65f1`, moved it through `In Progress` to `Resolved`, and saw both transitions with timestamps. An Open sample ticket displayed “No status changes have been recorded for this ticket.” API tests verify empty history data and malformed/nonexistent IDs. |

**Product Owner QA:** Pending. The Product Owner should repeat these checks
and record their own results before Gate C can pass.
