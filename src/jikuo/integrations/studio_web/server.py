"""Local read-only HTTP console for JIKUO Studio."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse

if __package__:
    from ...studio import document_rules, global_status
else:  # pragma: no cover - direct module execution fallback
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from jikuo.studio import document_rules, global_status


STUDIO_WEB_SCHEMA = "jikuo.studio.web_console.v0"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


INDEX_HTML = """<!doctype html>
<html lang="en" data-jikuo-studio="guarded-control-shell">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JIKUO Studio</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fa;
      --ink: #17202a;
      --muted: #607080;
      --line: #d9dee5;
      --panel: #ffffff;
      --accent: #1f7a68;
      --warn: #9a5b00;
      --danger: #9d2634;
      --soft: #eef3f1;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      letter-spacing: 0;
    }
    header {
      padding: 20px 28px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      display: flex;
      gap: 16px;
      align-items: center;
      justify-content: space-between;
    }
    h1 {
      margin: 0;
      font-size: 24px;
      line-height: 1.2;
      font-weight: 700;
    }
    main {
      width: min(1280px, 100%);
      margin: 0 auto;
      padding: 24px 28px 40px;
    }
    .status {
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      padding: 5px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      color: var(--muted);
      font-size: 14px;
      white-space: nowrap;
    }
    .status.available { color: var(--accent); }
    .status.degraded { color: var(--warn); }
    .status.unavailable { color: var(--danger); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }
    section {
      margin: 0 0 22px;
    }
    h2 {
      margin: 0 0 10px;
      font-size: 17px;
      line-height: 1.3;
    }
    .metric, .row {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      min-width: 0;
    }
    .metric b {
      display: block;
      font-size: 22px;
      line-height: 1.2;
      margin-bottom: 4px;
    }
    .metric span, .row p {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }
    .split {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }
    .row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: start;
    }
    .row h3 {
      margin: 0 0 4px;
      font-size: 15px;
      line-height: 1.3;
    }
    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }
    .section-title h2 {
      margin: 0;
    }
    .subhead {
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    code {
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      background: #eef1f4;
      padding: 2px 5px;
      border-radius: 4px;
      word-break: break-word;
    }
    a { color: #1d5f8a; }
    .mono { font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace; }
    .plan-tool {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      margin: 14px 0 0;
    }
    .plan-tool h3 {
      margin: 0 0 10px;
      font-size: 15px;
      line-height: 1.3;
    }
    .form-grid {
      display: grid;
      grid-template-columns: minmax(160px, 0.8fr) minmax(220px, 1.2fr) minmax(160px, 0.7fr);
      gap: 10px;
      align-items: end;
    }
    label {
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    input, select {
      width: 100%;
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font: inherit;
      font-size: 13px;
      padding: 7px 9px;
    }
    .plan-rule-row {
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto;
      gap: 10px;
      align-items: end;
      margin-top: 10px;
    }
    .plan-apply-row {
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto;
      gap: 10px;
      align-items: end;
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid var(--line);
    }
    button {
      min-height: 36px;
      border: 1px solid #176555;
      border-radius: 6px;
      background: var(--accent);
      color: #fff;
      font: inherit;
      font-size: 13px;
      font-weight: 650;
      padding: 7px 12px;
      cursor: pointer;
    }
    button:disabled {
      border-color: var(--line);
      background: #ccd4da;
      cursor: not-allowed;
    }
    .plan-result {
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }
    pre {
      margin: 0;
      padding: 12px;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: var(--soft);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      line-height: 1.45;
    }
    @media (max-width: 700px) {
      header { align-items: flex-start; flex-direction: column; }
      main { padding: 18px 16px 32px; }
      .row { grid-template-columns: 1fr; }
      .split { grid-template-columns: 1fr; }
      .form-grid, .plan-rule-row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>JIKUO Studio</h1>
    <span id="global-status" class="status">Loading</span>
  </header>
  <main>
    <section class="grid" id="overview"></section>
    <section>
      <div class="section-title">
        <h2 id="document-rules-title">Document Rules</h2>
        <span id="document-mounts-status" class="status">Loading</span>
      </div>
      <p class="subhead" id="document-rules-description"></p>
      <div class="grid" id="document-mounts-metrics"></div>
      <div class="split">
        <div>
          <p class="subhead" id="completion-checks-label">Completion checks</p>
          <div class="list" id="document-mounts-completion"></div>
        </div>
        <div>
          <p class="subhead" id="editable-configuration-label">Editable configuration</p>
          <div class="list" id="document-mounts-editable-sources"></div>
          <p class="subhead" id="governance-guidance-label" style="margin-top: 12px;">Governance guidance</p>
          <div class="list" id="document-mounts-guidance-sources"></div>
        </div>
      </div>
      <div class="plan-tool" aria-labelledby="document-rules-plan-title">
        <h3 id="document-rules-plan-title">Preview a Document Rules change</h3>
        <form id="document-rules-form">
          <div class="form-grid">
            <label>
              Change type
              <select id="document-rules-operation">
                <option value="add_context_doc">Add context document</option>
                <option value="add_completion_check">Add completion check</option>
                <option value="add_governance_reference">Add rule source</option>
                <option value="remove_context_doc">Remove context document</option>
                <option value="remove_completion_check">Remove completion check</option>
                <option value="remove_governance_reference">Remove rule source</option>
              </select>
            </label>
            <label>
              Project document path
              <input id="document-rules-path" name="path" placeholder="docs/example.md" autocomplete="off">
            </label>
            <label>
              Optional role name
              <input id="document-rules-role" name="role" placeholder="project_brief" autocomplete="off">
            </label>
          </div>
          <div class="plan-rule-row">
            <label>
              Completion check rule
              <input id="document-rules-completion-rule" name="completion_rule" placeholder="review this document before declaring the governed slice complete" autocomplete="off">
            </label>
            <button id="document-rules-preview-button" type="submit">Preview plan</button>
          </div>
        </form>
        <div class="plan-result" id="document-rules-plan-result" aria-live="polite"></div>
        <div class="plan-apply-row">
          <label>
            Approval phrase
            <input id="document-rules-approval-phrase" name="approval_phrase" placeholder="Approve Document Rules update" autocomplete="off">
          </label>
          <button id="document-rules-apply-button" type="button" disabled>Apply update</button>
        </div>
      </div>
    </section>
    <section>
      <h2>Panels</h2>
      <div class="list" id="panels"></div>
    </section>
    <section>
      <h2>Available Actions</h2>
      <div class="list" id="actions"></div>
    </section>
    <section>
      <h2>Diagnostics</h2>
      <div class="list" id="diagnostics"></div>
    </section>
  </main>
  <script>
    const text = (value) => value === null || value === undefined ? "" : String(value);
    const statusClass = (value) => `status ${text(value).replace(/[^a-z_]/g, "")}`;
    const row = (title, detail, status) => {
      const item = document.createElement("div");
      item.className = "row";
      item.innerHTML = `<div><h3></h3><p></p></div><span></span>`;
      item.querySelector("h3").textContent = title;
      item.querySelector("p").textContent = detail;
      const badge = item.querySelector("span");
      badge.className = statusClass(status || "available");
      badge.textContent = status || "available";
      return item;
    };
    const metric = (value, label) => {
      const item = document.createElement("div");
      item.className = "metric";
      item.innerHTML = `<b></b><span></span>`;
      item.querySelector("b").textContent = text(value);
      item.querySelector("span").textContent = label;
      return item;
    };
    const emptyRow = (message) => row("No issues", message, "available");
    const termsById = (items) => Object.fromEntries((items || []).map((item) => [item.term_id, item]));
    const termLabel = (terms, id, fallback) => (terms[id] && terms[id].user_label) || fallback;
    const termDescription = (terms, id, fallback) => (terms[id] && terms[id].user_description) || fallback;
    let currentDocumentRulesPlan = null;
    const addPlanMessage = (title, detail, status) => {
      const result = document.getElementById("document-rules-plan-result");
      result.replaceChildren(row(title, detail, status));
    };
    const updateApplyButton = () => {
      const button = document.getElementById("document-rules-apply-button");
      const phrase = document.getElementById("document-rules-approval-phrase").value.trim();
      button.disabled = !(currentDocumentRulesPlan && currentDocumentRulesPlan.status === "review" && phrase === "Approve Document Rules update");
    };
    const renderPlanPreview = (plan) => {
      currentDocumentRulesPlan = plan;
      const result = document.getElementById("document-rules-plan-result");
      const status = plan.status || "unknown";
      const summaryStatus = status === "refused" ? "unavailable" : (status === "review" ? "degraded" : "available");
      const summary = row(`Plan ${status}`, `Changes: ${plan.change_count || 0}; writes performed: ${String(Boolean(plan.writes_performed))}`, summaryStatus);
      const diff = document.createElement("pre");
      const diffPreview = plan.diff_preview || [];
      diff.textContent = diffPreview.length ? diffPreview.join("\\n") : "No document-rule changes proposed.";
      const validation = plan.validation || {};
      const validationRows = [
        ...(validation.errors || []).map((item) => row(item.code || "error", item.message || "", "unavailable")),
        ...(validation.warnings || []).map((item) => row(item.code || "warning", item.message || "", "degraded")),
        ...(validation.noops || []).map((item) => row(item.code || "noop", item.message || "", "available")),
      ];
      const approval = plan.approval || {};
      const approvalRow = row(
        "Approval boundary",
        approval.required ? "Guarded apply is required before any document rules are changed." : "No guarded apply is required for this preview result.",
        approval.required ? "degraded" : "available"
      );
      result.replaceChildren(summary, diff, ...validationRows, approvalRow);
      updateApplyButton();
    };
    const renderApplyResult = (result) => {
      const container = document.getElementById("document-rules-plan-result");
      const status = result.status || "unknown";
      const summaryStatus = status === "applied" ? "available" : "unavailable";
      const summary = row(`Apply ${status}`, `Write performed: ${String(Boolean(result.write_performed))}`, summaryStatus);
      const operations = document.createElement("pre");
      const applied = result.applied_operations || [];
      const refusals = result.refusal_reasons || [];
      operations.textContent = applied.length
        ? applied.map((item) => `${item.operation}: ${item.path || item.role || ""}`).join("\\n")
        : (refusals.length ? refusals.map((item) => `refused: ${item}`).join("\\n") : "No operations reported.");
      container.append(summary, operations);
      if (status === "applied") {
        currentDocumentRulesPlan = null;
        document.getElementById("document-rules-approval-phrase").value = "";
        updateApplyButton();
        fetch("/api/status", {cache: "no-store"}).then((response) => response.json()).then(render);
      }
    };
    const requestFromDocumentRulesForm = () => {
      const operation = document.getElementById("document-rules-operation").value;
      const path = document.getElementById("document-rules-path").value.trim();
      const role = document.getElementById("document-rules-role").value.trim();
      const completionRule = document.getElementById("document-rules-completion-rule").value.trim();
      if (!path) {
        return null;
      }
      const payload = {
        add_context_docs: [],
        remove_context_docs: [],
        add_completion_checks: [],
        remove_completion_checks: [],
        add_governance_references: [],
        remove_governance_references: [],
      };
      if (completionRule) {
        payload.completion_update_rule = completionRule;
      }
      if (operation === "add_context_doc") {
        payload.add_context_docs.push(role ? `${role}=${path}` : path);
      } else if (operation === "remove_context_doc") {
        payload.remove_context_docs.push(path);
      } else if (operation === "add_completion_check") {
        payload.add_completion_checks.push(path);
      } else if (operation === "remove_completion_check") {
        payload.remove_completion_checks.push(path);
      } else if (operation === "add_governance_reference") {
        payload.add_governance_references.push(path);
      } else if (operation === "remove_governance_reference") {
        payload.remove_governance_references.push(path);
      }
      return payload;
    };
    const renderDocumentMounts = (data) => {
      const summaries = data.summaries || {};
      const mounts = summaries.document_mounts || {};
      const terms = termsById(mounts.configuration_terms);
      document.getElementById("document-rules-title").textContent = termLabel(terms, "document_rules", "Document Rules");
      document.getElementById("document-rules-description").textContent = termDescription(
        terms,
        "document_rules",
        "Which project documents JIKUO should use as context, checks, and governance references."
      );
      document.getElementById("completion-checks-label").textContent = termLabel(terms, "completion_checks", "Completion checks");
      document.getElementById("editable-configuration-label").textContent = termLabel(terms, "editable_configuration", "Editable configuration");
      document.getElementById("governance-guidance-label").textContent = termLabel(terms, "governance_guidance", "Governance guidance");
      const status = document.getElementById("document-mounts-status");
      status.className = statusClass(mounts.status || "unavailable");
      status.textContent = mounts.status || "unavailable";
      const metrics = document.getElementById("document-mounts-metrics");
      metrics.replaceChildren(
        metric(mounts.role_count || 0, "Document roles"),
        metric(mounts.checked_document_count || 0, "Completion documents"),
        metric(mounts.missing_required_role_count || 0, "Missing required roles"),
        metric(mounts.mount_set_count || 0, "Rule sets")
      );
      const completion = document.getElementById("document-mounts-completion");
      const completionDocs = (mounts.checked_before_slice_completion || []).slice(0, 8);
      completion.replaceChildren(...(completionDocs.length ? completionDocs.map((item) =>
        row(item.path || "unbound", item.update_required_when || "", item.status || "available")
      ) : [emptyRow("No completion-check documents are configured.")]));
      const actions = data.available_actions || [];
      const planAction = actions.find((item) => item.action_id === "studio.document_mounts.plan_update") || {};
      const editableSources = document.getElementById("document-mounts-editable-sources");
      const editableRows = (mounts.editable_configuration_sources || []).map((item) =>
        row(item.path || "unbound", `${item.user_description || ""} ${termLabel(terms, "edit_status", "How changes are applied")}: ${planAction.disabled_reason || "preview now, guarded apply later"}`, planAction.status || "available")
      );
      editableSources.replaceChildren(...(editableRows.length ? editableRows : [
        row("No editable configuration source", "Document Rules has no structured configuration target.", "unavailable")
      ]));
      const guidanceSources = document.getElementById("document-mounts-guidance-sources");
      const guidanceRows = (mounts.governance_guidance_sources || []).map((item) =>
        row(item.path || "unbound", item.user_description || "Read as context; not edited by Document Rules.", "available")
      );
      const missing = mounts.missing_required_roles || [];
      guidanceSources.replaceChildren(
        ...(guidanceRows.length ? guidanceRows : [emptyRow("No governance guidance source is configured.")]),
        ...(missing.length ? missing.slice(0, 4).map((item) =>
          row(item.role || "missing role", item.path || "unbound", "warning")
        ) : [])
      );
    };
    const render = (data) => {
      const global = document.getElementById("global-status");
      global.className = statusClass(data.status);
      global.textContent = `${data.status} · no-write`;
      const summaries = data.summaries || {};
      const runtime = summaries.runtime || {};
      const policy = summaries.policy_management || {};
      const policyCounts = policy.summary_counts || {};
      const integrations = summaries.integrations || {};
      const mcp = integrations.mcp || {};
      const overview = document.getElementById("overview");
      overview.replaceChildren(
        metric(runtime.status || "unknown", "Runtime"),
        metric((summaries.document_mounts || {}).checked_document_count || 0, "Completion docs"),
        metric(policyCounts.active_policy_count || 0, "Active policies"),
        metric(policyCounts.package_template_count || 0, "Package templates"),
        metric(mcp.tool_count || 0, "MCP tools"),
        metric((data.pending_user_decisions || []).length, "Pending decisions"),
        metric((data.diagnostics || []).length, "Diagnostics")
      );
      renderDocumentMounts(data);
      const panels = document.getElementById("panels");
      panels.replaceChildren(...(data.panels || []).map((panel) =>
        row(panel.title || panel.panel_id, `${panel.provider_ref || ""} · ${panel.privacy_level || ""}`, panel.status)
      ));
      const actions = document.getElementById("actions");
      actions.replaceChildren(...(data.available_actions || []).map((action) =>
        row(action.title || action.action_id, `${action.write_mode || ""} · ${action.plan_surface || ""}`, action.status)
      ));
      const diagnostics = document.getElementById("diagnostics");
      const items = data.diagnostics || [];
      diagnostics.replaceChildren(...(items.length ? items : [{code: "ok", message: "No diagnostics reported.", severity: "available"}]).map((item) =>
        row(item.code || "diagnostic", item.message || "", item.severity || "available")
      ));
    };
    fetch("/api/status", {cache: "no-store"})
      .then((response) => response.json())
      .then(render)
      .catch((error) => {
        const global = document.getElementById("global-status");
        global.className = "status unavailable";
        global.textContent = "unavailable";
        document.getElementById("diagnostics").replaceChildren(row("fetch_failed", error.message, "error"));
      });
    document.getElementById("document-rules-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const payload = requestFromDocumentRulesForm();
      if (!payload) {
        addPlanMessage("Path required", "Enter a project-relative document path before previewing a plan.", "unavailable");
        return;
      }
      const button = document.getElementById("document-rules-preview-button");
      button.disabled = true;
      button.textContent = "Previewing";
      fetch("/api/document-rules/plan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload),
      })
        .then((response) => response.json())
        .then(renderPlanPreview)
        .catch((error) => addPlanMessage("Preview failed", error.message, "unavailable"))
        .finally(() => {
          button.disabled = false;
          button.textContent = "Preview plan";
        });
    });
    document.getElementById("document-rules-approval-phrase").addEventListener("input", updateApplyButton);
    document.getElementById("document-rules-apply-button").addEventListener("click", () => {
      const phrase = document.getElementById("document-rules-approval-phrase").value.trim();
      const button = document.getElementById("document-rules-apply-button");
      if (!currentDocumentRulesPlan) {
        addPlanMessage("Plan required", "Preview and review a Document Rules plan before applying.", "unavailable");
        return;
      }
      button.disabled = true;
      button.textContent = "Applying";
      fetch("/api/document-rules/apply", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          plan: currentDocumentRulesPlan,
          confirm_apply: true,
          approval_phrase: phrase,
        }),
      })
        .then((response) => response.json())
        .then(renderApplyResult)
        .catch((error) => addPlanMessage("Apply failed", error.message, "unavailable"))
        .finally(() => {
          button.textContent = "Apply update";
          updateApplyButton();
        });
    });
  </script>
</body>
</html>
"""


def json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def api_document_rules_plan_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "document rules plan requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    completion_update_rule = request_payload.get("completion_update_rule")
    if completion_update_rule is not None:
        completion_update_rule = str(completion_update_rule).strip() or None
    plan = document_rules.build_document_rules_update_plan(
        project_root=project_root,
        add_context_docs=string_list(request_payload.get("add_context_docs")),
        remove_context_docs=string_list(request_payload.get("remove_context_docs")),
        add_completion_checks=string_list(request_payload.get("add_completion_checks")),
        remove_completion_checks=string_list(request_payload.get("remove_completion_checks")),
        add_governance_references=string_list(request_payload.get("add_governance_references")),
        remove_governance_references=string_list(
            request_payload.get("remove_governance_references")
        ),
        completion_update_rule=completion_update_rule,
    )
    plan["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/document-rules/plan",
        "method": "POST",
        "write_mode": "no-write-plan",
        "writes_performed": False,
        "write_allowed_by_command": False,
    }
    return HTTPStatus.OK, plan


def api_document_rules_apply_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "document rules apply requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    result, _exit_code = document_rules.apply_document_rules_update_plan(
        request_payload.get("plan"),
        project_root=project_root,
        confirmed=bool(request_payload.get("confirm_apply")),
        approval_phrase=str(request_payload.get("approval_phrase") or "").strip() or None,
    )
    result["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/document-rules/apply",
        "method": "POST",
        "write_mode": "guarded",
        "writes_performed": bool(result.get("write_performed")),
        "write_allowed_by_command": bool(result.get("write_allowed_by_command")),
    }
    return HTTPStatus.OK, result


def api_payload_for_path(path: str, *, project_root: Path | None = None) -> tuple[int, dict[str, Any]]:
    parsed = urlparse(path)
    route = parsed.path.rstrip("/") or "/"
    if route == "/api/status":
        return HTTPStatus.OK, global_status.build_global_status(project_root=project_root)
    if route == "/api/panels":
        status = global_status.build_global_status(project_root=project_root)
        return HTTPStatus.OK, status.get("panel_registry") or {}
    if route == "/api/actions":
        status = global_status.build_global_status(project_root=project_root)
        return HTTPStatus.OK, status.get("action_registry") or {}
    if route == "/api/health":
        return HTTPStatus.OK, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "available",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    return HTTPStatus.NOT_FOUND, {
        "schema": STUDIO_WEB_SCHEMA,
        "status": "not_found",
        "path": parsed.path,
        "writes_performed": False,
        "write_allowed_by_command": False,
    }


def render_index_html() -> str:
    return INDEX_HTML


def make_handler(project_root: Path | None = None) -> type[BaseHTTPRequestHandler]:
    class StudioWebHandler(BaseHTTPRequestHandler):
        server_version = "JIKUOStudio/0"

        def _send(
            self,
            *,
            status: int,
            body: bytes,
            content_type: str,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            route = (urlparse(self.path).path.rstrip("/") or "/")
            if route in {"/", "/index.html"}:
                self._send(
                    status=HTTPStatus.OK,
                    body=render_index_html().encode("utf-8"),
                    content_type="text/html; charset=utf-8",
                )
                return
            if route.startswith("/api"):
                status, payload = api_payload_for_path(self.path, project_root=project_root)
                self._send(
                    status=status,
                    body=json_bytes(payload),
                    content_type="application/json; charset=utf-8",
                )
                return
            status, payload = api_payload_for_path(self.path, project_root=project_root)
            self._send(
                status=status,
                body=json_bytes(payload),
                content_type="application/json; charset=utf-8",
            )

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            route = (urlparse(self.path).path.rstrip("/") or "/")
            if route not in {"/api/document-rules/plan", "/api/document-rules/apply"}:
                status, payload = api_payload_for_path(self.path, project_root=project_root)
                self._send(
                    status=status,
                    body=json_bytes(payload),
                    content_type="application/json; charset=utf-8",
                )
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                content_length = 0
            if content_length > 65536:
                self._send(
                    status=HTTPStatus.BAD_REQUEST,
                    body=json_bytes(
                        {
                            "schema": STUDIO_WEB_SCHEMA,
                            "status": "invalid_request",
                            "message": "request body is too large",
                            "writes_performed": False,
                            "write_allowed_by_command": False,
                        }
                    ),
                    content_type="application/json; charset=utf-8",
                )
                return
            try:
                raw_body = self.rfile.read(content_length).decode("utf-8")
                request_payload = json.loads(raw_body or "{}")
            except json.JSONDecodeError as exc:
                self._send(
                    status=HTTPStatus.BAD_REQUEST,
                    body=json_bytes(
                        {
                            "schema": STUDIO_WEB_SCHEMA,
                            "status": "invalid_json",
                            "message": str(exc),
                            "writes_performed": False,
                            "write_allowed_by_command": False,
                        }
                    ),
                    content_type="application/json; charset=utf-8",
                )
                return
            if route == "/api/document-rules/plan":
                status, payload = api_document_rules_plan_payload(
                    request_payload,
                    project_root=project_root,
                )
            else:
                status, payload = api_document_rules_apply_payload(
                    request_payload,
                    project_root=project_root,
                )
            self._send(
                status=status,
                body=json_bytes(payload),
                content_type="application/json; charset=utf-8",
            )

        def log_message(self, _format: str, *args: Any) -> None:
            return

    return StudioWebHandler


def create_server(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    project_root: Path | None = None,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(project_root=project_root))


def serve(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    project_root: Path | None = None,
) -> int:
    httpd = create_server(host=host, port=port, project_root=project_root)
    actual_host, actual_port = httpd.server_address
    print(f"JIKUO Studio no-write console: http://{actual_host}:{actual_port}/")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping JIKUO Studio.")
    finally:
        httpd.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local JIKUO Studio web console.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--host", default=DEFAULT_HOST)
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve_parser.add_argument("--project-root", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        return serve(host=args.host, port=args.port, project_root=args.project_root)
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
