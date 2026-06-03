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
    from ...studio import document_rules, global_status, project_files
else:  # pragma: no cover - direct module execution fallback
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from jikuo.studio import document_rules, global_status, project_files


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
    .status.ok { color: var(--accent); }
    .status.review, .status.not_evaluated { color: var(--warn); }
    .status.refused { color: var(--danger); }
    .status.aligned { color: var(--accent); }
    .status.partial_trace, .status.no_trace { color: var(--warn); }
    .status.no_changes { color: var(--warn); }
    .status.needs_attention { color: var(--danger); }
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
    .file-picker {
      display: grid;
      gap: 10px;
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid var(--line);
    }
    .rules-overview {
      display: grid;
      gap: 12px;
      margin: 12px 0 16px;
    }
    .trace-layout {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }
    .trace-panel {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      padding: 10px;
      min-width: 0;
    }
    .trace-panel h3 {
      margin: 0 0 3px;
      font-size: 14px;
    }
    .trace-group {
      min-width: 0;
      padding: 10px 0 0 10px;
      border-top: 1px solid var(--line);
      border-left: 3px solid #b8c8d6;
    }
    .trace-group:first-child {
      padding-top: 0;
      border-top: 0;
    }
    .trace-group-title {
      display: grid;
      gap: 2px;
      margin: 0 0 7px -10px;
      padding: 5px 8px;
      background: var(--soft);
      border-left: 3px solid var(--accent);
    }
    .trace-group-title strong {
      color: var(--accent);
      font-size: 13px;
      line-height: 1.3;
    }
    .trace-group-title span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    .trace-summary {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 10px 0;
    }
    .trace-round-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 8px;
      margin: 10px 0;
    }
    .round-button {
      display: grid;
      gap: 5px;
      min-height: 72px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      text-align: left;
      padding: 9px 10px;
    }
    .round-button.selected {
      border-color: #7bb2a5;
      background: #eef8f4;
    }
    .round-button strong {
      display: block;
      overflow-wrap: anywhere;
      font-size: 13px;
    }
    .round-button span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    .trace-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
    .trace-badge {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      background: #fff;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
    }
    .trace-badge.trace-yes, .trace-badge.changes-yes {
      border-color: #8db8ac;
      color: #176555;
      background: #eef8f4;
    }
    .trace-badge.trace-no, .trace-badge.changes-no {
      color: var(--warn);
      background: #fff8ec;
    }
    .trace-chip {
      min-width: 150px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      padding: 8px 10px;
    }
    .trace-chip strong {
      display: block;
      font-size: 13px;
      color: var(--ink);
    }
    .trace-chip span {
      display: block;
      margin-top: 2px;
      color: var(--muted);
      font-size: 12px;
    }
    .trace-timeline {
      margin-top: 10px;
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }
    .trace-timeline h3 {
      margin: 0 0 8px;
      font-size: 14px;
    }
    .rules-groups {
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .rules-group {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      padding: 10px;
      min-width: 0;
    }
    .rules-group h3 {
      margin: 0 0 3px;
      font-size: 14px;
    }
    .rules-group .subhead {
      margin: 0 0 8px;
    }
    .compact-list {
      display: grid;
      gap: 6px;
    }
    .compact-item {
      min-width: 0;
      padding: 7px 0;
      border-top: 1px solid var(--line);
    }
    .compact-item:first-child {
      border-top: 0;
      padding-top: 0;
    }
    .compact-item strong {
      display: block;
      overflow-wrap: anywhere;
      font-size: 13px;
    }
    .compact-item span {
      color: var(--muted);
      display: block;
      font-size: 12px;
      line-height: 1.4;
      margin-top: 2px;
      overflow-wrap: anywhere;
    }
    .compact-expander {
      min-width: 0;
      border-top: 1px solid var(--line);
    }
    .compact-expander:first-child {
      border-top: 0;
    }
    .compact-toggle {
      width: 100%;
      min-height: auto;
      border: 0;
      border-radius: 0;
      background: transparent;
      color: var(--accent);
      display: block;
      padding: 7px 0;
      text-align: left;
      font: inherit;
      cursor: pointer;
    }
    .compact-toggle strong {
      display: block;
      font-size: 13px;
      line-height: 1.35;
    }
    .compact-toggle span {
      color: var(--muted);
      display: block;
      font-size: 12px;
      line-height: 1.4;
      margin-top: 2px;
      overflow-wrap: anywhere;
    }
    .compact-toggle:hover strong {
      text-decoration: underline;
    }
    .compact-expanded {
      display: grid;
      gap: 0;
      margin: 0 0 4px;
      padding-left: 10px;
      border-left: 2px solid var(--line);
    }
    .compact-expanded[hidden] {
      display: none;
    }
    .file-toolbar {
      display: grid;
      grid-template-columns: minmax(200px, 1fr) auto;
      gap: 10px;
      align-items: end;
    }
    .file-list {
      display: grid;
      gap: 6px;
      max-height: 260px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      padding: 8px;
    }
    .file-row {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) auto;
      gap: 8px;
      align-items: start;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
    }
    .file-row input {
      width: auto;
      min-height: auto;
      margin-top: 3px;
    }
    .file-meta {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }
    .file-membership {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 3px;
    }
    .membership-badge {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      padding: 2px 7px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
    }
    .membership-badge.in-rules {
      border-color: #8db8ac;
      color: #176555;
      background: #eef8f4;
    }
    .membership-badge.not-in-rules {
      color: #6b7280;
      background: #f8fafc;
    }
    .selected-files {
      display: grid;
      gap: 6px;
    }
    .selected-file {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--soft);
    }
    .secondary-button {
      border-color: var(--line);
      background: #fff;
      color: var(--ink);
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
      .trace-layout { grid-template-columns: 1fr; }
      .rules-groups { grid-template-columns: 1fr; }
      .form-grid, .plan-rule-row, .file-toolbar { grid-template-columns: 1fr; }
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
      <div class="rules-overview" aria-labelledby="document-rules-overview-title">
        <h3 id="document-rules-overview-title">Current Document Rules</h3>
        <p class="subhead">Each column is one Document Rules purpose. The rows inside that column are the documents currently configured for that purpose.</p>
        <div class="rules-groups">
          <div class="rules-group">
            <h3>Context documents</h3>
            <p class="subhead">Used before or during work as project context. Source: document roles.</p>
            <div class="compact-list" id="document-rules-context-overview"></div>
          </div>
          <div class="rules-group">
            <h3>Completion checks</h3>
            <p class="subhead">Checked before claiming a governed slice is complete. Source: completion-check rules.</p>
            <div class="compact-list" id="document-rules-completion-overview"></div>
          </div>
          <div class="rules-group">
            <h3>Governance references</h3>
            <p class="subhead">Explain boundaries and editable configuration. Source: rule-source references.</p>
            <div class="compact-list" id="document-rules-guidance-overview"></div>
          </div>
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
          <div class="file-picker" aria-labelledby="project-files-title">
            <h3 id="project-files-title">Add files to Document Rules</h3>
            <p class="subhead">Candidate local files. This is not the current mount set; each row shows current Document Rules membership.</p>
            <div class="file-toolbar">
              <label>
                Filter available files
                <input id="document-rules-file-filter" placeholder="path, role, membership..." autocomplete="off">
              </label>
              <button class="secondary-button" id="document-rules-clear-selection" type="button">Clear selection</button>
            </div>
            <div class="file-list" id="document-rules-file-list" aria-live="polite"></div>
            <p class="subhead">Selected files</p>
            <div class="selected-files" id="document-rules-selected-files"></div>
          </div>
        </form>
        <div class="plan-result" id="document-rules-plan-result" aria-live="polite"></div>
        <div class="plan-apply-row">
          <p class="subhead" id="document-rules-apply-note">Preview and review a plan to enable approval.</p>
          <button id="document-rules-apply-button" type="button" disabled>Approve and apply</button>
        </div>
      </div>
    </section>
    <section>
      <div class="section-title">
        <h2>Round Document Trace</h2>
        <span id="round-trace-status" class="status">Loading</span>
      </div>
      <p class="subhead">Select a runtime round to inspect expected documents, observed evidence, write activity, and gaps.</p>
      <div class="trace-round-list" id="round-trace-rounds"></div>
      <div class="trace-summary" id="round-trace-summary"></div>
      <div class="trace-layout">
        <div class="trace-panel">
          <h3>Expected</h3>
          <p class="subhead">Document and artifact obligations projected for this round.</p>
          <div class="compact-list" id="round-trace-expected"></div>
        </div>
        <div class="trace-panel">
          <h3>Observed</h3>
          <p class="subhead">Runtime evidence and planned or actual writes captured for the round.</p>
          <div class="compact-list" id="round-trace-observed"></div>
        </div>
        <div class="trace-panel">
          <h3>Gaps</h3>
          <p class="subhead">Missing or mismatched read/write evidence that needs attention.</p>
          <div class="compact-list" id="round-trace-gaps"></div>
        </div>
      </div>
      <div class="trace-timeline">
        <h3>Action chain</h3>
        <div class="compact-list" id="round-trace-timeline"></div>
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
    const compactItem = (title, detail) => {
      const item = document.createElement("div");
      item.className = "compact-item";
      item.innerHTML = `<strong></strong><span></span>`;
      item.querySelector("strong").textContent = title;
      item.querySelector("span").textContent = detail || "";
      return item;
    };
    const traceGroup = (title, detail, rows) => {
      const group = document.createElement("div");
      group.className = "trace-group";
      group.innerHTML = `<div class="trace-group-title"><strong></strong><span></span></div><div class="compact-list"></div>`;
      group.querySelector("strong").textContent = title;
      group.querySelector("span").textContent = detail || "";
      group.querySelector(".compact-list").replaceChildren(...(rows || []));
      return group;
    };
    const overflowNote = (count, shown, label, hiddenRows) => {
      const hidden = Math.max(0, count - shown);
      if (!hidden) {
        return null;
      }
      const rows = hiddenRows || [];
      if (!rows.length) {
        return compactItem(`+ ${hidden} more`, `${label} are configured but hidden in this preview.`);
      }
      const wrapper = document.createElement("div");
      wrapper.className = "compact-expander";
      const button = document.createElement("button");
      button.type = "button";
      button.className = "compact-toggle";
      button.innerHTML = `<strong></strong><span></span>`;
      const title = button.querySelector("strong");
      const detail = button.querySelector("span");
      const expanded = document.createElement("div");
      expanded.className = "compact-expanded";
      expanded.hidden = true;
      expanded.replaceChildren(...rows);
      const setExpanded = (open) => {
        expanded.hidden = !open;
        button.setAttribute("aria-expanded", String(open));
        title.textContent = open ? `Hide ${hidden} ${label}` : `+ ${hidden} more`;
        detail.textContent = open ? "Collapse hidden rows." : `Show hidden ${label}.`;
      };
      button.addEventListener("click", () => setExpanded(expanded.hidden));
      setExpanded(false);
      wrapper.append(button, expanded);
      return wrapper;
    };
    const numberValue = (value) => Number.isFinite(Number(value)) ? Number(value) : 0;
    const detailCount = (count, label) => `${numberValue(count)} ${label}`;
    const gapRows = (items, fallback) => {
      const records = items || [];
      const rows = records.slice(0, 4).map((item) =>
        compactItem(item.gap_type || "gap", item.path || "path not supplied")
      );
      const hiddenRows = records.slice(4).map((item) =>
        compactItem(item.gap_type || "gap", item.path || "path not supplied")
      );
      const extra = overflowNote(records.length, rows.length, "gaps", hiddenRows);
      return rows.length ? [...rows, ...(extra ? [extra] : [])] : [compactItem("No gaps", fallback)];
    };
    const termsById = (items) => Object.fromEntries((items || []).map((item) => [item.term_id, item]));
    const termLabel = (terms, id, fallback) => (terms[id] && terms[id].user_label) || fallback;
    const termDescription = (terms, id, fallback) => (terms[id] && terms[id].user_description) || fallback;
    const DOCUMENT_RULES_APPROVAL_PHRASE = "Approve Document Rules update";
    let currentDocumentRulesPlan = null;
    let projectFileItems = [];
    let selectedRoundTraceId = null;
    const selectedFileRecords = new Map();
    const addPlanMessage = (title, detail, status) => {
      const result = document.getElementById("document-rules-plan-result");
      result.replaceChildren(row(title, detail, status));
    };
    const updateApplyButton = () => {
      const button = document.getElementById("document-rules-apply-button");
      const note = document.getElementById("document-rules-apply-note");
      const ready = currentDocumentRulesPlan && currentDocumentRulesPlan.status === "review";
      button.disabled = !ready;
      button.textContent = "Approve and apply";
      note.textContent = ready
        ? "This will ask for confirmation before writing .jikuo/project_context.yaml."
        : "Preview and review a plan to enable approval.";
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
        updateApplyButton();
        fetch("/api/status", {cache: "no-store"}).then((response) => response.json()).then(render);
      }
    };
    const membershipParts = (membership) => {
      const parts = [];
      if (membership && membership.is_context_document) {
        parts.push(`Context document: ${(membership.context_role_refs || []).join(", ")}`);
      }
      if (membership && membership.is_completion_check) {
        parts.push("Completion check");
      }
      if (membership && membership.is_governance_reference) {
        parts.push("Governance reference");
      }
      return parts;
    };
    const membershipSummary = (membership) => {
      const parts = membershipParts(membership);
      return parts.length ? parts.join(" / ") : "Not in Document Rules";
    };
    const membershipState = (membership) => {
      return membershipParts(membership).length ? "In Document Rules" : "Not in Document Rules";
    };
    const appendMembershipBadges = (container, membership) => {
      const state = document.createElement("span");
      const parts = membershipParts(membership);
      state.className = `membership-badge ${parts.length ? "in-rules" : "not-in-rules"}`;
      state.textContent = membershipState(membership);
      container.append(state);
      parts.forEach((part) => {
        const badge = document.createElement("span");
        badge.className = "membership-badge in-rules";
        badge.textContent = part;
        container.append(badge);
      });
    };
    const renderSelectedFiles = () => {
      const container = document.getElementById("document-rules-selected-files");
      const records = Array.from(selectedFileRecords.values());
      if (!records.length) {
        container.replaceChildren(row("No files selected", "Use the project document list or type a single path.", "available"));
        return;
      }
      container.replaceChildren(...records.map((record) => {
        const item = document.createElement("div");
        item.className = "selected-file";
        const details = document.createElement("div");
        details.innerHTML = `<strong></strong><div class="file-meta"></div>`;
        details.querySelector("strong").textContent = record.path;
        details.querySelector(".file-meta").textContent = `selected at ${record.selected_at_utc}`;
        const remove = document.createElement("button");
        remove.className = "secondary-button";
        remove.type = "button";
        remove.textContent = "Remove";
        remove.addEventListener("click", () => {
          selectedFileRecords.delete(record.path);
          renderProjectFiles();
          renderSelectedFiles();
        });
        item.append(details, remove);
        return item;
      }));
    };
    const setSelectedPath = (path, selected) => {
      if (selected) {
        if (!selectedFileRecords.has(path)) {
          selectedFileRecords.set(path, {path, selected_at_utc: new Date().toISOString()});
        }
      } else {
        selectedFileRecords.delete(path);
      }
      renderSelectedFiles();
    };
    const renderProjectFiles = () => {
      const list = document.getElementById("document-rules-file-list");
      const filter = document.getElementById("document-rules-file-filter").value.trim().toLowerCase();
      const filtered = projectFileItems.filter((item) =>
        !filter || `${item.path} ${item.file_kind} ${membershipSummary(item.document_rules_membership)} ${membershipState(item.document_rules_membership)}`.toLowerCase().includes(filter)
      ).slice(0, 120);
      if (!filtered.length) {
        list.replaceChildren(row("No available files", "No matching markdown, YAML, JSON, or text files were found.", "degraded"));
        return;
      }
      list.replaceChildren(...filtered.map((item) => {
        const record = document.createElement("label");
        record.className = "file-row";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = selectedFileRecords.has(item.path);
        checkbox.addEventListener("change", () => setSelectedPath(item.path, checkbox.checked));
        const details = document.createElement("div");
        details.innerHTML = `<strong></strong><div class="file-meta"></div><div class="file-membership"></div>`;
        details.querySelector("strong").textContent = item.path;
        details.querySelector(".file-meta").textContent =
          `${item.file_kind} / modified ${item.modified_at_utc}`;
        appendMembershipBadges(details.querySelector(".file-membership"), item.document_rules_membership);
        const badge = document.createElement("span");
        badge.className = "status available";
        badge.textContent = item.file_kind || "file";
        record.append(checkbox, details, badge);
        return record;
      }));
    };
    const loadProjectFiles = () => {
      fetch("/api/project-files", {cache: "no-store"})
        .then((response) => response.json())
        .then((inventory) => {
          projectFileItems = inventory.items || [];
          renderProjectFiles();
          renderSelectedFiles();
        })
        .catch((error) => {
          document.getElementById("document-rules-file-list").replaceChildren(
            row("Project documents unavailable", error.message, "unavailable")
          );
          renderSelectedFiles();
        });
    };
    const requestFromDocumentRulesForm = () => {
      const operation = document.getElementById("document-rules-operation").value;
      const path = document.getElementById("document-rules-path").value.trim();
      const role = document.getElementById("document-rules-role").value.trim();
      const completionRule = document.getElementById("document-rules-completion-rule").value.trim();
      const selectedPaths = Array.from(selectedFileRecords.keys());
      const paths = selectedPaths.length ? selectedPaths : (path ? [path] : []);
      if (!paths.length) {
        return null;
      }
      const payload = {
        add_context_docs: [],
        remove_context_docs: [],
        add_completion_checks: [],
        remove_completion_checks: [],
        add_governance_references: [],
        remove_governance_references: [],
        selection_records: Array.from(selectedFileRecords.values()),
      };
      if (completionRule) {
        payload.completion_update_rule = completionRule;
      }
      if (operation === "add_context_doc") {
        payload.add_context_docs.push(...paths.map((item) => role && paths.length === 1 ? `${role}=${item}` : item));
      } else if (operation === "remove_context_doc") {
        payload.remove_context_docs.push(...paths);
      } else if (operation === "add_completion_check") {
        payload.add_completion_checks.push(...paths);
      } else if (operation === "remove_completion_check") {
        payload.remove_completion_checks.push(...paths);
      } else if (operation === "add_governance_reference") {
        payload.add_governance_references.push(...paths);
      } else if (operation === "remove_governance_reference") {
        payload.remove_governance_references.push(...paths);
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
      const contextOverview = document.getElementById("document-rules-context-overview");
      const roles = mounts.roles || [];
      const contextRows = roles.slice(0, 6).map((item) =>
        compactItem(item.path || "unbound", `role: ${item.role || "unlabeled"}${item.note ? ` / ${item.note}` : ""}`)
      );
      const contextHiddenRows = roles.slice(6).map((item) =>
        compactItem(item.path || "unbound", `role: ${item.role || "unlabeled"}${item.note ? ` / ${item.note}` : ""}`)
      );
      const contextOverflow = overflowNote(roles.length, contextRows.length, "context documents", contextHiddenRows);
      contextOverview.replaceChildren(...(contextRows.length ? contextRows : [compactItem("No context documents", "No document roles are configured.")]), ...(contextOverflow ? [contextOverflow] : []));
      const completionOverview = document.getElementById("document-rules-completion-overview");
      const completionOverviewDocs = mounts.checked_before_slice_completion || [];
      const completionRows = completionOverviewDocs.slice(0, 6).map((item) =>
        compactItem(item.path || "unbound", item.update_required_when || "review before declaring the slice complete")
      );
      const completionHiddenRows = completionOverviewDocs.slice(6).map((item) =>
        compactItem(item.path || "unbound", item.update_required_when || "review before declaring the slice complete")
      );
      const completionOverflow = overflowNote(completionOverviewDocs.length, completionRows.length, "completion checks", completionHiddenRows);
      completionOverview.replaceChildren(...(completionRows.length ? completionRows : [compactItem("No completion checks", "No completion-check documents are configured.")]), ...(completionOverflow ? [completionOverflow] : []));
      const guidanceOverview = document.getElementById("document-rules-guidance-overview");
      const guidanceOverviewRows = (mounts.document_rule_sources || []).map((item) =>
        compactItem(item.path || "unbound", `${item.user_label || item.source_kind || "source"} / ${item.user_description || ""}`)
      );
      guidanceOverview.replaceChildren(...(guidanceOverviewRows.length ? guidanceOverviewRows : [compactItem("No governance references", "No rule sources are configured.")]));
    };
    const traceChip = (title, detail) => {
      const item = document.createElement("div");
      item.className = "trace-chip";
      item.innerHTML = `<strong></strong><span></span>`;
      item.querySelector("strong").textContent = title;
      item.querySelector("span").textContent = detail || "";
      return item;
    };
    const artifactPath = (item) => text((item || {}).path || (item || {}).path_ref || (item || {}).ref || (item || {}).target || (item || {}).source_ref || "path not supplied");
    const artifactDetail = (item, fallback) => {
      const record = item || {};
      const evidenceParts = [
        record.operation,
        record.source_kind,
        record.evidence_status,
        record.attribution_status,
        record.git_status ? `git ${record.git_status}` : "",
        record.previous_path ? `from ${record.previous_path}` : "",
        record.trigger ? `trigger ${record.trigger.type || "write"}` : "",
        record.trigger_count ? `${record.trigger_count} triggers` : "",
      ].filter(Boolean);
      const reason = text(record.reason || record.applicability_reason || record.role || record.source_ref || fallback || "");
      return [evidenceParts.join(" / "), reason].filter(Boolean).join(" / ");
    };
    const artifactRows = (items, fallback, detailFallback, counted, noun) => {
      const records = items || [];
      const rows = records.slice(0, 5).map((item) =>
        compactItem(artifactPath(item), artifactDetail(item, detailFallback))
      );
      const hiddenRows = records.slice(5).map((item) =>
        compactItem(artifactPath(item), artifactDetail(item, detailFallback))
      );
      const extra = overflowNote(records.length, rows.length, "trace items", hiddenRows);
      if (rows.length) {
        return [...rows, ...(extra ? [extra] : [])];
      }
      const total = numberValue(counted);
      if (total > 0) {
        return [compactItem(`${total} ${noun || "items"} counted`, "Detailed item paths are not available in this history card.")];
      }
      return [compactItem("None captured", fallback)];
    };
    const traceGapRows = (items, fallback, counted) => {
      const records = items || [];
      const rows = records.slice(0, 6).map((item) => {
        const nested = (item || {}).observed || (item || {}).expected || {};
        const nestedDetail = artifactDetail(nested, "");
        const detail = [artifactPath(item), nestedDetail].filter(Boolean).join(" / ");
        return compactItem(item.gap_type || "gap", detail);
      });
      const hiddenRows = records.slice(6).map((item) => {
        const nested = (item || {}).observed || (item || {}).expected || {};
        const nestedDetail = artifactDetail(nested, "");
        const detail = [artifactPath(item), nestedDetail].filter(Boolean).join(" / ");
        return compactItem(item.gap_type || "gap", detail);
      });
      const extra = overflowNote(records.length, rows.length, "gaps", hiddenRows);
      if (rows.length) {
        return [...rows, ...(extra ? [extra] : [])];
      }
      const total = numberValue(counted);
      if (total > 0) {
        return [compactItem(`${total} gaps counted`, "Detailed gap paths are not available in this history card.")];
      }
      return [compactItem("No gaps reported", fallback)];
    };
    const artifactList = (items) => Array.isArray(items) ? items : [];
    const firstArtifactList = (...sources) => {
      for (const source of sources) {
        if (Array.isArray(source) && source.length) {
          return source;
        }
      }
      for (const source of sources) {
        if (Array.isArray(source)) {
          return source;
        }
      }
      return [];
    };
    const hasCountValue = (value) => value !== null && value !== undefined && value !== "";
    const artifactCount = (items, ...counts) => {
      for (const count of counts) {
        if (hasCountValue(count)) {
          return numberValue(count);
        }
      }
      return Array.isArray(items) ? items.length : 0;
    };
    const traceState = (round, active, gapReport) => {
      if (!round || !round.has_document_trace) {
        return {key: "no_trace", label: "No trace captured"};
      }
      if (!round.has_document_changes) {
        return {key: "no_changes", label: "No document changes"};
      }
      if ((active.status || "") === "ok" && numberValue((gapReport || {}).gap_count) === 0) {
        return {key: "aligned", label: "Aligned"};
      }
      if ((active.status || "") === "review" || numberValue((gapReport || {}).gap_count) > 0) {
        return {key: "needs_attention", label: "Needs attention"};
      }
      return {key: "partial_trace", label: "Partial trace"};
    };
    const roundButton = (round, selected, data) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `round-button${selected ? " selected" : ""}`;
      button.innerHTML = `<strong></strong><span></span><div class="trace-badges"></div>`;
      button.querySelector("strong").textContent = round.label || round.round_id || "runtime round";
      const counts = round.counts || {};
      button.querySelector("span").textContent = `${round.lifecycle_event || "unknown event"} / ${numberValue(counts.required_companion_write_count)} required / ${numberValue(counts.declared_write_count || counts.planned_write_count)} declared / ${numberValue(counts.actual_write_count)} actual`;
      const badges = button.querySelector(".trace-badges");
      const traceBadge = document.createElement("span");
      traceBadge.className = `trace-badge ${round.has_document_trace ? "trace-yes" : "trace-no"}`;
      traceBadge.textContent = round.has_document_trace ? "Trace" : "No trace";
      const changeBadge = document.createElement("span");
      changeBadge.className = `trace-badge ${round.has_document_changes ? "changes-yes" : "changes-no"}`;
      changeBadge.textContent = round.has_document_changes ? "Changes" : "No changes";
      badges.append(traceBadge, changeBadge);
      button.addEventListener("click", () => {
        selectedRoundTraceId = round.round_id;
        renderRoundDocumentTrace(data);
      });
      return button;
    };
    const renderRoundDocumentTrace = (data) => {
      const summaries = data.summaries || {};
      const traceList = (summaries.runtime || {}).round_document_traces || {};
      const rounds = traceList.rounds || [];
      const defaultRoundId = traceList.default_round_id || (rounds[0] || {}).round_id;
      if (!selectedRoundTraceId || !rounds.some((round) => round.round_id === selectedRoundTraceId)) {
        selectedRoundTraceId = defaultRoundId || null;
      }
      const selectedRound = rounds.find((round) => round.round_id === selectedRoundTraceId) || null;
      const latestRuntimeRound = rounds.find((round) => round.round_id === traceList.latest_runtime_round_id) || (rounds[0] || null);
      const latestReceiptRound = rounds.find((round) => round.round_id === traceList.latest_completion_receipt_round_id) || null;
      const selectedCounts = (selectedRound || {}).counts || {};
      const selectedSemantic = (selectedRound || {}).semantic_intent_coverage || {};
      const activeTrace = (selectedRound || {}).artifact_assurance || {};
      const latestAvailable = Boolean(selectedRound && selectedRound.has_document_trace && activeTrace.schema);
      const active = latestAvailable ? activeTrace : {};
      const activeRead = (active || {}).read_assurance || {};
      const activeWrite = (active || {}).write_assurance || {};
      const activeGap = (active || {}).gap_report || {};
      const runtimeProjection = activeTrace.runtime_projection || {};
      const companionProjection = runtimeProjection.companion_write_obligations || {};
      const statusState = traceState(selectedRound, active, activeGap);
      const status = document.getElementById("round-trace-status");
      status.className = statusClass(statusState.key);
      status.textContent = statusState.label;
      const roundList = document.getElementById("round-trace-rounds");
      roundList.replaceChildren(
        ...(rounds.length
          ? rounds.map((round) => roundButton(round, round.round_id === selectedRoundTraceId, data))
          : [compactItem("No runtime rounds", "Run a card-producing JIKUO proposal to capture runtime rounds.")])
      );

      const expectedReads = artifactList(activeRead.required_read_set);
      const readEvidence = artifactList(activeRead.read_evidence_set);
      const expectedWrites = artifactList(activeWrite.required_write_set);
      const requiredCompanionWrites = artifactList(activeWrite.required_companion_write_set);
      const completionCandidates = firstArtifactList(activeWrite.completion_check_candidates, activeWrite.write_candidate_set);
      const plannedWrites = artifactList(activeWrite.planned_write_set);
      const declaredWrites = firstArtifactList(activeWrite.declared_write_set, activeWrite.planned_write_set);
      const actualWrites = artifactList(activeWrite.actual_write_set);
      const actualWriteSource = runtimeProjection.actual_write_source || "";
      const actualWriteGroupTitle = actualWriteSource === "git_status_observed" ? "Git-observed actual writes" : "Actual writes";
      const actualWriteFallback = actualWriteSource === "git_status_observed"
        ? "No git-observed actual write evidence was supplied for this round."
        : "No actual write evidence was supplied for this round.";
      const companionTriggers = artifactList(companionProjection.triggers);
      const companionIgnoredItems = artifactList(companionProjection.ignored_items);
      const readGaps = firstArtifactList(activeGap.read_gaps, activeRead.required_not_read);
      const writeGapFallbacks = [
        ...(activeWrite.required_not_planned || []),
        ...(activeWrite.required_not_written || []),
        ...(activeWrite.planned_not_written || []),
        ...(activeWrite.unplanned_written || []),
      ];
      const writeGaps = firstArtifactList(activeGap.write_gaps, writeGapFallbacks);
      const completionNotEvaluated = artifactList(activeWrite.completion_check_not_evaluated);
      const requiredReadCount = artifactCount(activeRead.required_read_set, activeRead.required_read_count, selectedCounts.required_read_count);
      const readEvidenceCount = artifactCount(activeRead.read_evidence_set, activeRead.read_evidence_count, selectedCounts.read_evidence_count);
      const expectedWriteCount = artifactCount(activeWrite.required_write_set, activeWrite.required_write_count, selectedCounts.required_write_count);
      const requiredCompanionWriteCount = artifactCount(
        activeWrite.required_companion_write_set,
        activeWrite.required_companion_write_count,
        selectedCounts.required_companion_write_count
      );
      const completionCandidateCount = artifactCount(
        activeWrite.completion_check_candidates || activeWrite.write_candidate_set,
        activeWrite.completion_check_candidate_count,
        selectedCounts.completion_check_candidate_count
      );
      const plannedWriteCount = artifactCount(activeWrite.planned_write_set, activeWrite.planned_write_count, selectedCounts.planned_write_count);
      const declaredWriteCount = artifactCount(
        activeWrite.declared_write_set || activeWrite.planned_write_set,
        activeWrite.declared_write_count,
        selectedCounts.declared_write_count,
        activeWrite.planned_write_count,
        selectedCounts.planned_write_count
      );
      const actualWriteCount = artifactCount(activeWrite.actual_write_set, activeWrite.actual_write_count, selectedCounts.actual_write_count);
      const companionTriggerCount = artifactCount(companionProjection.triggers, activeWrite.companion_trigger_count, companionProjection.trigger_count, selectedCounts.companion_trigger_count);
      const companionIgnoredCount = artifactCount(companionProjection.ignored_items, activeWrite.companion_ignored_item_count, companionProjection.ignored_item_count, selectedCounts.companion_ignored_item_count);
      const readGapCount = artifactCount(activeGap.read_gaps || activeRead.required_not_read, activeGap.read_gap_count, activeRead.required_reads_without_evidence_count);
      const writeGapCount = artifactCount(activeGap.write_gaps, activeGap.write_gap_count);
      const gapCount = artifactCount(null, activeGap.gap_count, selectedCounts.gap_count);
      const uncategorizedGapCount = Math.max(0, gapCount - readGapCount - writeGapCount);
      const completionNotEvaluatedCount = artifactCount(
        activeWrite.completion_check_not_evaluated,
        activeGap.completion_check_not_evaluated_count,
        activeWrite.completion_check_not_evaluated_count,
        selectedCounts.completion_check_not_evaluated_count
      );

      document.getElementById("round-trace-summary").replaceChildren(
        traceChip("Latest runtime turn", latestRuntimeRound ? (latestRuntimeRound.label || latestRuntimeRound.round_id) : "no runtime round"),
        traceChip("Latest completion receipt", latestReceiptRound ? (latestReceiptRound.label || latestReceiptRound.round_id) : "No completion receipt"),
        traceChip("Selected round", selectedRound ? (selectedRound.label || selectedRound.round_id) : "no runtime round"),
        traceChip("Trace source", selectedRound ? `${selectedRound.source_kind || "runtime"} / ${selectedRound.trace_label || ""}` : "no runtime evidence"),
        traceChip("Document changes", selectedRound ? selectedRound.document_change_label : "No document trace"),
        traceChip("Semantic intent", selectedRound
          ? `${selectedSemantic.coverage_status || "unknown"} / ${selectedSemantic.provider || "provider unavailable"}`
          : "No semantic evidence"),
        traceChip("Expected reads", detailCount(requiredReadCount, "documents")),
        traceChip("Observed reads", detailCount(readEvidenceCount, "evidence items")),
        traceChip("Writes", `${requiredCompanionWriteCount} required / ${declaredWriteCount} declared / ${actualWriteCount} actual`),
        traceChip("Gaps", detailCount(gapCount, "items")),
        traceChip("Unchecked applicability", detailCount(completionNotEvaluatedCount, "items"))
      );

      document.getElementById("round-trace-expected").replaceChildren(
        traceGroup("Read obligations", detailCount(requiredReadCount, "documents"), [
          ...artifactRows(expectedReads, "No required reads are configured for this selected round.", "configured context document", requiredReadCount, "documents"),
        ]),
        traceGroup("Required companion writes", detailCount(requiredCompanionWriteCount, "documents"), [
          ...artifactRows(requiredCompanionWrites, "No required companion writes were projected for this selected round.", "required companion write", requiredCompanionWriteCount, "required companion writes"),
        ]),
        traceGroup("Applicable writes", detailCount(expectedWriteCount, "documents"), [
          ...artifactRows(expectedWrites, "No applicable required writes are known for this selected round.", "required write", expectedWriteCount, "documents"),
        ]),
        traceGroup("Completion-check candidates", detailCount(completionCandidateCount, "candidates"), [
          ...artifactRows(completionCandidates, "No completion-check candidates are configured for this selected round.", "completion check candidate", completionCandidateCount, "candidates"),
        ])
      );

      document.getElementById("round-trace-observed").replaceChildren(
        ...(latestAvailable
          ? [
              traceGroup("Runtime source", "Projection and observation provenance", [
                compactItem("Runtime projection", `${runtimeProjection.event || selectedRound.lifecycle_event || "latest task"} / ${runtimeProjection.persistence || selectedRound.source_kind || "runtime summary"}`),
                compactItem("History card", selectedRound.history_ref || "history ref not supplied"),
                compactItem("Actual write source", actualWriteSource || "source not supplied"),
                compactItem("Git observation", runtimeProjection.git_write_observation
                  ? `${runtimeProjection.git_write_observation.status || "unknown"} / ${numberValue(runtimeProjection.git_write_observation.observed_actual_write_count)} observed / ${runtimeProjection.git_write_observation.attribution_status || "attribution not supplied"}`
                  : "not supplied for this round"),
              ]),
              traceGroup("Companion projection", companionProjection.schema
                ? `${companionProjection.status || "unknown"} / ${requiredCompanionWriteCount} required / ${companionTriggerCount} triggers / ${companionIgnoredCount} ignored`
                : "not supplied for this round", [
                ...artifactRows(companionTriggers, "No companion write triggers were projected for this round.", "companion write trigger", companionTriggerCount, "companion triggers"),
                ...artifactRows(companionIgnoredItems, "No actual writes were ignored by companion rules.", "ignored actual write", companionIgnoredCount, "ignored actual writes"),
              ]),
              traceGroup("Read evidence", detailCount(readEvidenceCount, "items"), [
                ...artifactRows(readEvidence, "No read evidence was supplied for this round.", "read evidence", readEvidenceCount, "read evidence items"),
              ]),
              traceGroup("Declared writes", detailCount(declaredWriteCount, "documents"), [
                compactItem("Declared actual writes", detailCount(runtimeProjection.declared_actual_write_count, "items")),
                ...artifactRows(declaredWrites, "No declared write evidence was supplied for this round.", "declared write", declaredWriteCount, "declared writes"),
              ]),
              traceGroup(actualWriteGroupTitle, detailCount(actualWriteCount, "documents"), [
                ...artifactRows(actualWrites, actualWriteFallback, "actual write", actualWriteCount, "actual writes"),
              ]),
            ]
          : [
              traceGroup("Runtime source", "No comparable document evidence", [
                compactItem("Runtime projection", selectedRound ? `${selectedRound.lifecycle_event || "runtime round"} has no comparable document trace.` : "No comparable trace was captured."),
                compactItem("Observed evidence", "No read/write evidence is available for this selected round."),
              ]),
            ])
      );

      const gapRowsForTrace = latestAvailable
        ? [
            ...traceGapRows(readGaps, "No required-read gaps are currently reported.", readGapCount),
            ...traceGapRows(writeGaps, "No write gaps are currently reported.", writeGapCount),
            ...(uncategorizedGapCount
              ? [compactItem(`${uncategorizedGapCount} total gaps counted`, "Detailed gap categories are not available in this history card.")]
              : []),
          ]
        : [compactItem("No comparable trace", "This selected round has no runtime document evidence to compare.")];
      document.getElementById("round-trace-gaps").replaceChildren(
        traceGroup("Read gaps", detailCount(readGapCount, "items"), [
          ...(latestAvailable ? traceGapRows(readGaps, "No required-read gaps are currently reported.", readGapCount) : gapRowsForTrace),
        ]),
        traceGroup("Write gaps", detailCount(writeGapCount + uncategorizedGapCount, "items"), [
          ...(latestAvailable
            ? [
                ...traceGapRows(writeGaps, "No write gaps are currently reported.", writeGapCount),
                ...(uncategorizedGapCount
                  ? [compactItem(`${uncategorizedGapCount} total gaps counted`, "Detailed gap categories are not available in this history card.")]
                  : []),
              ]
            : [compactItem("No comparable trace", "This selected round has no runtime document evidence to compare.")]),
        ]),
        traceGroup("Unchecked applicability", detailCount(completionNotEvaluatedCount, "completion checks"), [
          ...(completionNotEvaluatedCount
            ? artifactRows(completionNotEvaluated, "", "needs applicability decision evidence", completionNotEvaluatedCount, "completion checks")
            : [compactItem("No unchecked applicability", "No unevaluated completion-check applicability is reported.")]),
        ])
      );

      document.getElementById("round-trace-timeline").replaceChildren(
        compactItem("1. Round source", selectedRound ? `${selectedRound.lifecycle_event || "runtime round"} from ${selectedRound.source_kind || "runtime state"}` : "No runtime round selected."),
        compactItem("2. Expected documents", `${requiredReadCount} reads / ${completionCandidateCount} completion candidates`),
        compactItem("3. Observed evidence", `${readEvidenceCount} reads / ${requiredCompanionWriteCount} required writes / ${declaredWriteCount} declared writes / ${actualWriteCount} actual writes`),
        compactItem("4. Review result", statusState.label),
        compactItem("5. Semantic coverage", selectedSemantic.coverage_status
          ? `${selectedSemantic.coverage_status} / ${selectedSemantic.gap_reason || selectedSemantic.semantic_intent_status || "no gap"}`
          : "No semantic coverage projection for this round."),
        compactItem("6. Guarantee", active.guarantee || "evidence_comparison_only")
      );
    };
    const render = (data) => {
      const global = document.getElementById("global-status");
      global.className = statusClass(data.status);
      global.textContent = `${data.status} · no-write`;
      const summaries = data.summaries || {};
      const runtime = summaries.runtime || {};
      const semanticCoverage = runtime.semantic_intent_coverage || {};
      const policy = summaries.policy_management || {};
      const policyCounts = policy.summary_counts || {};
      const integrations = summaries.integrations || {};
      const mcp = integrations.mcp || {};
      const overview = document.getElementById("overview");
      overview.replaceChildren(
        metric(runtime.status || "unknown", "Runtime"),
        metric(semanticCoverage.coverage_status || "unknown", "Semantic intent"),
        metric((summaries.document_mounts || {}).checked_document_count || 0, "Completion docs"),
        metric(policyCounts.active_policy_count || 0, "Active policies"),
        metric(policyCounts.package_template_count || 0, "Package templates"),
        metric(mcp.tool_count || 0, "MCP tools"),
        metric((data.pending_user_decisions || []).length, "Pending decisions"),
        metric((data.diagnostics || []).length, "Diagnostics")
      );
      renderDocumentMounts(data);
      renderRoundDocumentTrace(data);
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
    loadProjectFiles();
    document.getElementById("document-rules-file-filter").addEventListener("input", renderProjectFiles);
    document.getElementById("document-rules-clear-selection").addEventListener("click", () => {
      selectedFileRecords.clear();
      renderProjectFiles();
      renderSelectedFiles();
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
    document.getElementById("document-rules-apply-button").addEventListener("click", () => {
      const button = document.getElementById("document-rules-apply-button");
      if (!currentDocumentRulesPlan) {
        addPlanMessage("Plan required", "Preview and review a Document Rules plan before applying.", "unavailable");
        return;
      }
      const changeCount = currentDocumentRulesPlan.change_count || 0;
      const confirmed = window.confirm(
        `Apply this Document Rules change?\n\nTarget: .jikuo/project_context.yaml\nChanges: ${changeCount}\n\nThis updates project configuration after guarded validation.`
      );
      if (!confirmed) {
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
          approval_phrase: DOCUMENT_RULES_APPROVAL_PHRASE,
          approval_source: "studio_confirmation_dialog",
        }),
      })
        .then((response) => response.json())
        .then(renderApplyResult)
        .catch((error) => addPlanMessage("Apply failed", error.message, "unavailable"))
        .finally(() => {
          button.textContent = "Approve and apply";
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
        "selection_records": request_payload.get("selection_records") or [],
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
    if route == "/api/project-files":
        return HTTPStatus.OK, project_files.build_project_file_inventory(
            project_root=project_root
        )
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
