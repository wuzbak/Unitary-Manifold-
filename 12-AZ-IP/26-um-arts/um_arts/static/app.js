/* SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
 * Copyright (C) 2026 ThomasCory Walker-Pearson */
"use strict";
const element = (id) => document.getElementById(id);
let token = "";
let selection = null;
let refreshing = false;

async function api(path, payload) {
  const options = {cache: "no-store", credentials: "same-origin"};
  if (payload) {
    options.method = "POST";
    options.headers = {"Content-Type": "application/json", "X-UM-ARTS-Token": token};
    options.body = JSON.stringify(payload);
  }
  const response = await fetch(path, options);
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || `HTTP ${response.status}`);
  return value;
}

function showError(error) { element("error").textContent = error.message; }
function showReport(value) { element("report").textContent = JSON.stringify(value, null, 2); }
function button(label, action) {
  const node = document.createElement("button");
  node.textContent = label;
  node.addEventListener("click", () => Promise.resolve().then(action).catch(showError));
  return node;
}
function row(label) {
  const node = document.createElement("li");
  const text = document.createElement("span");
  text.textContent = label;
  node.append(text);
  return node;
}

async function submit(action, id) {
  element("error").textContent = "";
  const payload = id ? {action, id} : {action};
  if (action === "run" || action === "resume") {
    const input = element("max-jobs");
    const budget = Number(input.value);
    if (!input.checkValidity() || !Number.isSafeInteger(budget) || budget < 1) {
      throw new Error("New jobs per slice must be a positive integer.");
    }
    payload.max_jobs = budget;
  }
  const task = await api("/api/tasks", payload);
  selection = {type: "tasks", id: task.id};
  showReport(task);
  await refresh();
}

async function inspect(artifact) {
  selection = {type: "artifacts", kind: artifact.kind, id: artifact.id};
  showReport(await api(`/api/artifacts/${artifact.kind}/${artifact.id}`));
  await updateSelection();
}

async function updateSelection() {
  if (!selection) return;
  const path = selection.type === "tasks" ? `/api/tasks/${selection.id}` :
    `/api/artifacts/${selection.kind}/${selection.id}`;
  if (selection.type === "tasks") showReport(await api(path));
  element("logs").textContent = (await api(`${path}/logs`)).text || "No log output yet.";
}

async function refresh() {
  if (refreshing) return;
  refreshing = true;
  try {
    const [health, tasks, artifacts] = await Promise.all([
      api("/api/health"), api("/api/tasks"), api("/api/artifacts")
    ]);
    element("connection").textContent = `Connected · ${health.version} · ${health.active_task ? "task running" : "idle"}`;
    element("tasks").replaceChildren();
    for (const task of tasks) {
      const budget = task.max_jobs === undefined ? "" : ` · new-job budget ${task.max_jobs}`;
      const item = row(`${task.action} · ${task.status}${budget} · ${task.id}`);
      item.append(button("View task & logs", async () => {
        selection = {type: "tasks", id: task.id};
        await updateSelection();
      }));
      element("tasks").append(item);
    }
    if (!tasks.length) element("tasks").append(row("No queued tasks."));
    element("artifacts").replaceChildren();
    for (const artifact of artifacts) {
      const item = row(`${artifact.kind} · ${artifact.evidence_kind} · ${artifact.status} (unverified list) · ${artifact.id}`);
      item.append(button("Inspect", () => inspect(artifact)));
      if (artifact.kind === "plans" || artifact.resumable) {
        item.append(button(artifact.kind === "plans" ? "Run plan" : "Resume attempt",
          () => submit(artifact.kind === "plans" ? "run" : "resume", artifact.id)));
      }
      element("artifacts").append(item);
    }
    if (!artifacts.length) element("artifacts").append(row("No artifacts. Collect a plan to begin."));
    await updateSelection();
  } catch (error) {
    element("connection").textContent = "Disconnected or request blocked";
    showError(error);
  } finally {
    refreshing = false;
  }
}

async function start() {
  try {
    token = (await api("/api/session")).token;
    const preflight = await api("/api/preflight");
    element("preflight").textContent = JSON.stringify(preflight, null, 2);
    element("plan").disabled = preflight.status !== "ready";
    element("plan").addEventListener("click", () => submit("plan").catch(showError));
    element("refresh").addEventListener("click", refresh);
    await refresh();
    window.setInterval(refresh, 2000);
  } catch (error) { showError(error); }
}
start();
