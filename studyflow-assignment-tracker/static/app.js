"use strict";

// The browser sends user input to Python; Python validates and saves it.
const byId = (id) => document.getElementById(id);
const form = byId("assignment-form");
const assignmentDialog = byId("assignment-dialog");
const deleteDialog = byId("delete-dialog");
const state = { assignments: [], stats: null, editing: null, deleting: null, request: 0 };
let searchTimer;
let toastTimer;

function element(tag, className = "", text = "") {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = text; // User-entered text is never interpreted as HTML.
  return node;
}

function icon(name) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.classList.add("icon");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", `/static/icons.svg#${name}`);
  svg.append(use);
  return svg;
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch {
    throw new Error("We couldn't connect to StudyFlow. Check that the Python server is running, then try again.");
  }
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("The server returned an unexpected response. Please try again.");
  }
  if (!response.ok) {
    const error = new Error(data.error || "Something went wrong. Please try again.");
    error.fields = data.fields || {};
    throw error;
  }
  return data;
}

function toast(message, isError = false) {
  clearTimeout(toastTimer);
  const notification = element("div", `toast${isError ? " error" : ""}`);
  notification.append(icon(isError ? "alert" : "check-circle"), element("span", "", message));
  byId("toast-region").replaceChildren(notification);
  toastTimer = setTimeout(() => byId("toast-region").replaceChildren(), isError ? 8000 : 4500);
}

function courseTone(course) {
  return [...course].reduce((total, character) => total + character.codePointAt(0), 0) % 4;
}

function formattedDate(value, options = { month: "short", day: "numeric", year: "numeric" }) {
  // Parse as a local calendar date; UTC parsing can move a deadline by a day.
  const [year, month, day] = value.split("-").map(Number);
  const localDate = new Date(0);
  localDate.setFullYear(year, month - 1, day);
  localDate.setHours(12, 0, 0, 0);
  return localDate.toLocaleDateString("en-US", options);
}

function relativeDate(assignment) {
  if (assignment.completed) return "Completed";
  const days = assignment.days_left;
  if (days < 0) return `${Math.abs(days)} day${days === -1 ? "" : "s"} overdue`;
  if (days === 0) return "Due today";
  if (days === 1) return "Due tomorrow";
  return `In ${days} days`;
}

function renderStats(data) {
  state.stats = data.stats;
  for (const name of ["total", "pending", "completed", "overdue"]) {
    byId(`stat-${name}`).textContent = data.stats[name];
  }
  byId("nav-total").textContent = data.stats.total;
  byId("nav-upcoming").textContent = data.stats.upcoming;
  const percent = data.stats.total ? Math.round(data.stats.completed / data.stats.total * 100) : 0;
  byId("completion-progress").value = percent;
  byId("completion-percent").textContent = `${percent}%`;
  byId("momentum-copy").textContent = data.stats.total
    ? `${data.stats.completed} of ${data.stats.total} assignments done. Every small step adds up.`
    : "Your next small step starts here.";
  byId("today-date").textContent = formattedDate(data.today, { weekday: "short", month: "short", day: "numeric", year: "numeric" });
  const next = data.next_assignment;
  byId("focus-title").textContent = next ? next.title : data.stats.total ? "Look at you go!" : "A fresh start awaits";
  byId("focus-details").textContent = next
    ? `${next.course} · ${formattedDate(next.due_date)}`
    : data.stats.total ? "All your assignments are complete. Take a well-earned breather." : "Add your first assignment and make a little room for focus.";
  byId("focus-badge").textContent = next ? relativeDate(next) : data.stats.total ? "All caught up" : "Let's get started";
}

function renderCourses(courses) {
  const current = byId("course-filter").value;
  const all = element("option", "", "All courses");
  all.value = "";
  byId("course-filter").replaceChildren(all);
  byId("course-suggestions").replaceChildren();
  const navigation = byId("sidebar-courses");
  navigation.replaceChildren();
  for (const course of courses) {
    const option = element("option", "", course);
    option.value = course;
    byId("course-filter").append(option);
    const suggestion = element("option");
    suggestion.value = course;
    byId("course-suggestions").append(suggestion);
    const link = element("button", `course-link tone-${courseTone(course)}${current === course ? " active" : ""}`);
    link.append(element("span", "course-dot"), element("span", "", course));
    link.addEventListener("click", () => {
      resetFilters(false);
      byId("course-filter").value = course;
      setNavigation("all");
      loadAssignments();
      byId("assignments-section").scrollIntoView({ behavior: "smooth", block: "start" });
    });
    navigation.append(link);
  }
  if (!courses.length) navigation.append(element("p", "sidebar-hint", "Your courses will appear here."));
  byId("course-filter").value = courses.includes(current) ? current : "";
  return current && !courses.includes(current);
}

function taskRow(assignment) {
  const row = element("article", `task-row is-${assignment.status}`);
  row.setAttribute("aria-label", assignment.title);
  const main = element("div", "task-main");
  const toggle = element("button", "complete-toggle");
  toggle.setAttribute("aria-pressed", String(assignment.completed));
  toggle.setAttribute("aria-label", `Mark ${assignment.title} as ${assignment.completed ? "pending" : "completed"}`);
  toggle.append(icon("check"));
  toggle.addEventListener("click", async () => {
    toggle.disabled = true;
    try {
      await api(`/api/assignments/${assignment.id}`, { method: "PATCH", body: JSON.stringify({ completed: !assignment.completed }) });
      toast(assignment.completed ? "Back on your list. One step at a time." : "Another one done. Nice work!");
      await loadAssignments();
    } catch (error) {
      toast(error.message, true);
    } finally {
      toggle.disabled = false;
    }
  });
  const details = element("div", "task-details");
  details.append(element("h3", "task-title", assignment.title));
  const statusLabels = { completed: "Completed", overdue: "Overdue", today: "Due today", upcoming: "Upcoming", pending: "Pending" };
  details.append(element("span", `task-status status-${assignment.status}`, statusLabels[assignment.status]));
  details.append(element("span", "mobile-detail", `${assignment.course} · ${assignment.priority[0].toUpperCase() + assignment.priority.slice(1)} priority`));
  if (assignment.notes) {
    const notes = element("p", "task-notes", assignment.notes);
    notes.title = assignment.notes;
    details.append(notes);
  }
  main.append(toggle, details);
  const courseCell = element("div", "task-course");
  const courseTag = element("span", `course-tag tone-${courseTone(assignment.course)}`);
  courseTag.append(element("span", "course-dot"), element("span", "", assignment.course));
  courseCell.append(courseTag);
  const due = element("div", "task-due");
  const time = element("time", "due-date", formattedDate(assignment.due_date));
  time.dateTime = assignment.due_date;
  due.append(time, element("span", "due-relative", relativeDate(assignment)));
  const priority = element("div", "task-priority");
  priority.append(element("span", `priority-badge priority-${assignment.priority}`, assignment.priority[0].toUpperCase() + assignment.priority.slice(1)));
  const actions = element("div", "task-actions");
  const edit = element("button", "icon-button");
  edit.setAttribute("aria-label", `Edit ${assignment.title}`);
  edit.title = "Edit assignment";
  edit.append(icon("edit"));
  edit.addEventListener("click", () => openAssignment(assignment));
  const remove = element("button", "icon-button delete-button");
  remove.setAttribute("aria-label", `Delete ${assignment.title}`);
  remove.title = "Delete assignment";
  remove.append(icon("trash"));
  remove.addEventListener("click", () => {
    state.deleting = assignment.id;
    byId("delete-title").textContent = assignment.title;
    byId("delete-error").hidden = true;
    deleteDialog.showModal();
  });
  actions.append(edit, remove);
  row.append(main, courseCell, due, priority, actions);
  return row;
}

function hasFilters() {
  return byId("search").value.trim() || byId("status-filter").value !== "all"
    || byId("priority-filter").value !== "all" || byId("course-filter").value;
}

function renderTasks(data) {
  state.assignments = data.assignments;
  const list = byId("task-list");
  list.replaceChildren();
  for (const assignment of data.assignments) list.append(taskRow(assignment));
  const count = data.assignments.length;
  byId("result-count").textContent = count;
  byId("results-summary").textContent = `Showing ${count} of ${data.stats.total} assignment${data.stats.total === 1 ? "" : "s"}`;
  byId("reset-filters").hidden = !hasFilters();
  if (!count) {
    const empty = element("div", "empty-state");
    const mark = element("div", "empty-icon");
    mark.append(icon(hasFilters() ? "search" : "book"));
    empty.append(mark, element("h3", "", hasFilters() ? "A little too quiet here" : "Great things start with a small step."));
    empty.append(element("p", "", hasFilters()
      ? "No assignments match these filters. Try a different search or clear your filters to see everything."
      : "Your study space is ready. Add your first assignment and take the guesswork out of your next deadline."));
    const action = element("button", `button ${hasFilters() ? "secondary" : "primary"}`, hasFilters() ? "Clear filters" : "Add your first assignment");
    action.addEventListener("click", () => hasFilters() ? resetFilters() : openAssignment());
    empty.append(action);
    list.append(empty);
  }
}

async function loadAssignments() {
  const requestNumber = ++state.request;
  byId("assignments-section").setAttribute("aria-busy", "true");
  const query = new URLSearchParams({
    q: byId("search").value.trim(), status: byId("status-filter").value,
    priority: byId("priority-filter").value, course: byId("course-filter").value, sort: byId("sort").value,
  });
  try {
    const data = await api(`/api/assignments?${query}`);
    if (requestNumber !== state.request) return;
    renderStats(data);
    if (renderCourses(data.courses)) return loadAssignments();
    renderTasks(data);
    byId("page-error").hidden = true;
    const notice = [data.import_notice, data.warning].filter(Boolean).join(" ");
    byId("notice").textContent = notice;
    byId("notice").hidden = !notice;
  } catch (error) {
    if (requestNumber !== state.request) return;
    byId("page-error-text").textContent = error.message;
    byId("page-error").hidden = false;
    if (!state.stats) {
      for (const name of ["total", "pending", "completed", "overdue"]) byId(`stat-${name}`).textContent = "—";
      byId("task-list").replaceChildren(element("div", "loading-state", "Your assignments couldn't be loaded. Use “Try again” above to reconnect."));
      byId("results-summary").textContent = "Waiting to reconnect";
    }
  } finally {
    if (requestNumber === state.request) byId("assignments-section").setAttribute("aria-busy", "false");
  }
}

function resetFilters(reload = true) {
  clearTimeout(searchTimer);
  byId("search").value = "";
  byId("status-filter").value = "all";
  byId("priority-filter").value = "all";
  byId("course-filter").value = "";
  byId("sort").value = "due_asc";
  if (reload) {
    setNavigation("all");
    loadAssignments();
  }
}

function setNavigation(view) {
  for (const button of document.querySelectorAll("[data-view]")) {
    const active = button.dataset.view === view;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  }
  const titles = { dashboard: "Overview", all: "All assignments", upcoming: "Upcoming", completed: "Completed" };
  byId("breadcrumb-page").textContent = titles[view] || "Assignments";
  byId("assignments-heading").firstChild.textContent = view === "upcoming" ? "Coming up next " : view === "completed" ? "Your completed work " : "Your assignments ";
}

function openAssignment(assignment = null) {
  state.editing = assignment ? assignment.id : null;
  form.reset();
  clearFormErrors();
  byId("dialog-title").textContent = assignment ? "Edit assignment" : "New assignment";
  byId("save-assignment").textContent = assignment ? "Save changes" : "Create assignment";
  for (const field of ["title", "course", "due_date", "priority", "notes"]) {
    if (assignment) form.elements.namedItem(field).value = assignment[field];
  }
  assignmentDialog.showModal();
  byId("title").focus();
}

function clearFormErrors() {
  byId("form-error").hidden = true;
  for (const node of form.querySelectorAll(".field-error")) node.textContent = "";
  for (const node of form.querySelectorAll("[aria-invalid]")) node.removeAttribute("aria-invalid");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFormErrors();
  const data = Object.fromEntries(new FormData(form).entries());
  const save = byId("save-assignment");
  save.disabled = true;
  save.textContent = "Saving…";
  try {
    const result = await api(state.editing ? `/api/assignments/${state.editing}` : "/api/assignments", {
      method: state.editing ? "PATCH" : "POST", body: JSON.stringify(data),
    });
    assignmentDialog.close();
    toast(result.message);
    await loadAssignments();
  } catch (error) {
    byId("form-error").textContent = error.message;
    byId("form-error").hidden = false;
    let firstInvalid = null;
    for (const [field, message] of Object.entries(error.fields || {})) {
      const input = form.elements.namedItem(field);
      const label = byId(`${field}-error`);
      if (input && label) {
        input.setAttribute("aria-invalid", "true");
        label.textContent = message;
        if (!firstInvalid) firstInvalid = input;
      }
    }
    (firstInvalid || byId("form-error")).focus();
  } finally {
    save.disabled = false;
    save.textContent = state.editing ? "Save changes" : "Create assignment";
  }
});

byId("confirm-delete").addEventListener("click", async () => {
  const button = byId("confirm-delete");
  button.disabled = true;
  try {
    const result = await api(`/api/assignments/${state.deleting}`, { method: "DELETE", body: JSON.stringify({ confirm: true }) });
    deleteDialog.close();
    toast(result.message);
    await loadAssignments();
  } catch (error) {
    byId("delete-error").textContent = error.message;
    byId("delete-error").hidden = false;
  } finally {
    button.disabled = false;
  }
});

for (const button of document.querySelectorAll("[data-close]")) {
  button.addEventListener("click", () => byId(button.dataset.close).close());
}
byId("add-assignment").addEventListener("click", () => openAssignment());
byId("retry").addEventListener("click", loadAssignments);
byId("reset-filters").addEventListener("click", () => resetFilters());
byId("view-upcoming").addEventListener("click", () => document.querySelector('[data-view="upcoming"]').click());
byId("search").addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadAssignments, 200);
});
for (const id of ["status-filter", "priority-filter", "course-filter", "sort"]) {
  byId(id).addEventListener("change", () => {
    setNavigation(byId("status-filter").value === "completed" ? "completed" : byId("status-filter").value === "upcoming" ? "upcoming" : "all");
    loadAssignments();
  });
}
for (const button of document.querySelectorAll("[data-view]")) {
  button.addEventListener("click", () => {
    resetFilters(false);
    const view = button.dataset.view;
    byId("status-filter").value = ["upcoming", "completed"].includes(view) ? view : "all";
    setNavigation(view);
    loadAssignments();
  });
}
for (const button of document.querySelectorAll("[data-stat]")) {
  button.addEventListener("click", () => {
    resetFilters(false);
    byId("status-filter").value = button.dataset.stat;
    setNavigation(button.dataset.stat === "completed" ? "completed" : "all");
    loadAssignments();
    byId("assignments-section").scrollIntoView({ behavior: "smooth", block: "start" });
  });
}
document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey
      && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)
      && !document.querySelector("dialog[open]")) {
    event.preventDefault();
    byId("search").focus();
  }
});
loadAssignments();
