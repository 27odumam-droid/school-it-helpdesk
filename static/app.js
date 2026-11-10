const $ = (selector, root = document) => root.querySelector(selector);

function showMessage(element, message, kind = "") {
  element.textContent = message;
  element.className = `message ${kind}`.trim();
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error?.message || `Request failed (${response.status}).`);
  }
  return body;
}

function addOption(select, value, label = value) {
  const option = document.createElement("option");
  option.value = value;
  option.textContent = label;
  select.append(option);
}

async function loadDashboard() {
  const form = $("#filters-form");
  const tableBody = $("#tickets-body");
  const message = $("#dashboard-message");

  async function refresh() {
    const query = new URLSearchParams(new FormData(form));
    for (const [key, value] of [...query.entries()]) {
      if (!value) query.delete(key);
    }
    try {
      const { tickets } = await requestJson(`/api/tickets?${query}`);
      tableBody.replaceChildren();
      const { technicians } = await requestJson("/api/technicians");
      for (const ticket of tickets) {
        const row = document.createElement("tr");
        const idCell = document.createElement("td");
        const link = document.createElement("a");
        link.href = `/tickets/${encodeURIComponent(ticket.id)}`;
        link.textContent = ticket.id.slice(0, 8);
        link.title = ticket.id;
        idCell.append(link);
        row.append(idCell);
        for (const value of [
          ticket.room,
          ticket.device,
          ticket.category,
          ticket.priority,
        ]) {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        }
        const statusCell = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = `status status-${ticket.status.toLowerCase().replace(" ", "-")}`;
        badge.textContent = ticket.status;
        statusCell.append(badge);
        row.append(statusCell);

        const assignmentCell = document.createElement("td");
        const assignmentForm = document.createElement("form");
        assignmentForm.className = "inline-form";
        const select = document.createElement("select");
        select.setAttribute("aria-label", `Technician for ticket ${ticket.id}`);
        addOption(select, "", "Unassigned");
        for (const technician of technicians) {
          addOption(select, technician.id, technician.name);
        }
        select.value = ticket.technician_id || "";
        const save = document.createElement("button");
        save.type = "submit";
        save.textContent = "Save";
        assignmentForm.append(select, save);
        assignmentForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          save.disabled = true;
          try {
            await requestJson(`/api/tickets/${encodeURIComponent(ticket.id)}/assignment`, {
              method: "PATCH",
              body: JSON.stringify({ technician_id: select.value || null }),
            });
            showMessage(message, "Assignment saved.", "success");
            await refresh();
          } catch (error) {
            showMessage(message, error.message, "error");
            save.disabled = false;
          }
        });
        assignmentCell.append(assignmentForm);
        row.append(assignmentCell);

        const createdCell = document.createElement("td");
        createdCell.textContent = new Date(ticket.created_at).toLocaleDateString();
        row.append(createdCell);
        tableBody.append(row);
      }
      showMessage(message, `${tickets.length} ticket${tickets.length === 1 ? "" : "s"} found.`);
    } catch (error) {
      showMessage(message, error.message, "error");
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    refresh();
  });
  $("#clear-filters").addEventListener("click", () => {
    form.reset();
    refresh();
  });
  refresh();
}

function loadNewTicketForm() {
  const form = $("#new-ticket-form");
  const message = $("#form-message");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    try {
      const { ticket } = await requestJson("/api/tickets", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showMessage(message, "Ticket created. Opening its details…", "success");
      window.location.assign(`/tickets/${encodeURIComponent(ticket.id)}`);
    } catch (error) {
      showMessage(message, error.message, "error");
    }
  });
}

async function loadTicketDetails() {
  const message = $("#details-message");
  const pageData = JSON.parse($("#ticket-page-data").textContent);
  let ticket;
  let technicians;
  let history;

  function getNextStatuses() {
    return ticket.status === "Open"
      ? ["In Progress"]
      : ticket.status === "In Progress" ? ["Resolved"] : [];
  }

  function displayTicket() {
    $("#ticket-title").textContent = `Ticket ${ticket.id.slice(0, 8)}`;
    const fields = $("#ticket-fields");
    fields.replaceChildren();
    const details = [
      ["Ticket ID", ticket.id],
      ["Room", ticket.room],
      ["Device", ticket.device],
      ["Category", ticket.category],
      ["Priority", ticket.priority],
      ["Status", ticket.status],
      ["Technician", ticket.assigned_technician || "Unassigned"],
      ["Created", new Date(ticket.created_at).toLocaleString()],
      ["Description", ticket.description],
      ["Resolution notes", ticket.resolution_notes || "Not resolved"],
      ["Resolved", ticket.resolved_at ? new Date(ticket.resolved_at).toLocaleString() : "—"],
    ];
    for (const [label, value] of details) {
      const group = document.createElement("div");
      const term = document.createElement("dt");
      term.textContent = label;
      const description = document.createElement("dd");
      description.textContent = value;
      if (label === "Status") {
        description.className = `status status-${ticket.status.toLowerCase().replace(" ", "-")}`;
      }
      group.append(term, description);
      fields.append(group);
    }

    const technicianSelect = $("#technician-select");
    technicianSelect.replaceChildren();
    addOption(technicianSelect, "", "Unassigned");
    for (const technician of technicians) {
      addOption(technicianSelect, technician.id, technician.name);
    }
    technicianSelect.value = ticket.technician_id || "";

    const statusSelect = $("#status-select");
    statusSelect.replaceChildren();
    const nextStatuses = getNextStatuses();
    addOption(statusSelect, ticket.status, `${ticket.status} (current)`);
    for (const status of nextStatuses) addOption(statusSelect, status);
    statusSelect.disabled = nextStatuses.length === 0;
    updateStatusForm(nextStatuses);
    $("#ticket-card").hidden = false;
    displayHistory();
  }

  function displayHistory() {
    const events = $("#history-events");
    events.replaceChildren();
    if (history.length === 0) {
      const empty = document.createElement("li");
      empty.className = "history-empty";
      empty.textContent = "No status changes have been recorded for this ticket.";
      events.append(empty);
      return;
    }

    for (const event of history) {
      const item = document.createElement("li");
      const description = document.createElement("p");
      description.textContent = `${event.old_status} → ${event.new_status}`;
      const timestamp = document.createElement("time");
      timestamp.dateTime = event.changed_at;
      timestamp.textContent = new Date(event.changed_at).toLocaleString();
      item.append(description, timestamp);
      events.append(item);
    }
  }

  function updateStatusForm(nextStatuses) {
    const statusSelect = $("#status-select");
    const submitButton = $("#status-form").querySelector("button[type=submit]");
    const canUpdate = nextStatuses.includes(statusSelect.value);
    const resolving = canUpdate && statusSelect.value === "Resolved";
    submitButton.disabled = !canUpdate;
    submitButton.textContent = nextStatuses.length
      ? "Save status"
      : "No further status changes";
    $("#resolution-notes-field").hidden = !resolving;
    $("#resolution-notes-field textarea").required = resolving;
  }

  try {
    const result = await Promise.all([
      requestJson("/api/technicians"),
      requestJson(`/api/tickets/${encodeURIComponent(pageData.ticket_id)}`),
      requestJson(`/api/tickets/${encodeURIComponent(pageData.ticket_id)}/history`),
    ]);
    technicians = result[0].technicians;
    ticket = result[1].ticket;
    history = result[2].history;
    displayTicket();
  } catch (error) {
    showMessage(message, error.message, "error");
    return;
  }

  $("#assignment-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const technicianId = $("#technician-select").value || null;
      const response = await requestJson(`/api/tickets/${encodeURIComponent(ticket.id)}/assignment`, {
        method: "PATCH",
        body: JSON.stringify({ technician_id: technicianId }),
      });
      ticket = response.ticket;
      displayTicket();
      showMessage(message, "Assignment saved.", "success");
    } catch (error) {
      showMessage(message, error.message, "error");
    }
  });

  $("#status-select").addEventListener("change", () => {
    updateStatusForm(getNextStatuses());
  });

  $("#status-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = { status: $("#status-select").value };
    const notes = new FormData(form).get("resolution_notes");
    if (notes) payload.resolution_notes = notes;
    try {
      const oldStatus = ticket.status;
      const response = await requestJson(`/api/tickets/${encodeURIComponent(ticket.id)}/status`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      ticket = response.ticket;
      history.push({
        old_status: oldStatus,
        new_status: ticket.status,
        changed_at: ticket.updated_at,
      });
      displayTicket();
      showMessage(message, "Status saved.", "success");
    } catch (error) {
      showMessage(message, error.message, "error");
    }
  });
}

if ($("#filters-form")) loadDashboard();
if ($("#new-ticket-form")) loadNewTicketForm();
if ($("#ticket-page-data")) loadTicketDetails();
