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
    from ... import policy_management_status, policy_store, policy_templates, project_state
    from ...studio import document_rules, global_status, project_files
else:  # pragma: no cover - direct module execution fallback
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from jikuo import policy_management_status, policy_store, policy_templates, project_state
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
      min-width: 0;
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
    .policy-action-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      min-width: 0;
    }
    .policy-action-buttons button {
      flex: 0 1 220px;
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
    .policy-metrics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin: 10px 0 14px;
    }
    .policy-columns {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 12px 0;
    }
    .policy-columns.policy-primary {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .policy-column {
      min-width: 0;
    }
    .policy-column h3 {
      margin: 0 0 4px;
      font-size: 14px;
    }
    .policy-detail-grid {
      display: grid;
      grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
      gap: 12px;
      margin: 12px 0;
      align-items: start;
    }
    .policy-detail-panel {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      padding: 12px;
      display: grid;
      gap: 10px;
    }
    .policy-detail-panel h3 {
      margin: 0;
      font-size: 15px;
      line-height: 1.35;
    }
    .policy-editor-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
      align-items: end;
    }
    .policy-editor-grid label,
    .policy-editor-grid .subhead {
      min-width: 0;
    }
    .policy-editor-note {
      margin: 0;
      align-self: center;
    }
    .policy-detail-header {
      display: grid;
      gap: 6px;
    }
    .policy-detail-header strong {
      font-size: 14px;
      overflow-wrap: anywhere;
    }
    .policy-detail-header span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
      overflow-wrap: anywhere;
    }
    .policy-record {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      padding: 10px;
      display: grid;
      gap: 7px;
    }
    .policy-record strong {
      display: block;
      overflow-wrap: anywhere;
      font-size: 13px;
      line-height: 1.35;
    }
    .policy-record p {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
      overflow-wrap: anywhere;
    }
    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
    .tag {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      padding: 2px 7px;
      font-size: 12px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }
    .tag.active, .tag.available, .tag.scope {
      border-color: #8db8ac;
      color: #176555;
      background: #eef8f4;
    }
    .tag.guarded, .tag.review {
      color: var(--warn);
      background: #fff8ec;
    }
    .option-group {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-content: start;
      min-width: 0;
      min-height: 36px;
    }
    .option-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 30px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      padding: 4px 9px;
      color: var(--ink);
      font-size: 12px;
      line-height: 1.2;
      cursor: pointer;
      max-width: 100%;
      overflow-wrap: anywhere;
    }
    .option-pill input {
      width: auto;
      min-height: auto;
      margin: 0;
      padding: 0;
    }
    .option-pill:has(input:checked) {
      border-color: #8db8ac;
      color: #176555;
      background: #eef8f4;
    }
    .option-pill.ignored {
      color: var(--muted);
      background: #f6f8fb;
      border-style: dashed;
      cursor: not-allowed;
      opacity: 0.72;
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
      .policy-columns { grid-template-columns: 1fr; }
      .policy-columns.policy-primary { grid-template-columns: 1fr; }
      .policy-detail-grid { grid-template-columns: 1fr; }
      .rules-groups { grid-template-columns: 1fr; }
      .form-grid, .plan-rule-row, .file-toolbar { grid-template-columns: 1fr; }
    }
    @media (max-width: 1180px) {
      .policy-detail-grid { grid-template-columns: 1fr; }
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
        <h2>Latest Semantic Classification</h2>
        <span id="semantic-evidence-status" class="status">Loading</span>
      </div>
      <p class="subhead">Latest retained host AI semantic intent when available, plus the latest runtime round and remaining evidence limits.</p>
      <div class="list" id="semantic-evidence-list"></div>
    </section>
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
      <div class="section-title">
        <h2>Policies And Templates</h2>
        <span id="policy-management-status" class="status">Loading</span>
      </div>
      <p class="subhead">No-write view of project policies, candidate proposals, package templates, starter packs, and guarded operation boundaries.</p>
      <div class="policy-metrics" id="policy-management-metrics"></div>
      <div class="plan-tool">
        <h3>Change active policy configuration</h3>
        <p class="subhead">Inspect the selected policy, preview controlled configuration changes, then apply them through a guarded writer.</p>
        <div class="policy-detail-grid">
          <div class="policy-detail-panel">
            <h3>Selected policy</h3>
            <label>Target policy
              <select id="policy-evolution-policy"></select>
            </label>
            <div class="policy-detail-header" id="policy-selected-summary"></div>
            <div class="tag-list" id="policy-selected-trigger-tags"></div>
            <div class="compact-list" id="policy-selected-config"></div>
          </div>
          <div class="policy-detail-panel">
            <h3>Proposed change</h3>
            <div class="policy-editor-grid">
              <label>Operation
                <select id="policy-evolution-operation">
                  <option value="refine_policy">Refine trigger conditions</option>
                  <option value="deprecate_policy">Deprecate policy</option>
                  <option value="supersede_policy">Supersede policy</option>
                </select>
              </label>
              <label>Feedback
                <select id="policy-evolution-feedback">
                  <option value="">No feedback label</option>
                  <option value="defer">Defer</option>
                  <option value="not_applicable">Not applicable</option>
                  <option value="needs_scope_narrowing">Needs scope narrowing</option>
                </select>
              </label>
              <label>Trigger mode
                <select id="policy-evolution-trigger-mode">
                  <option value="scope_first">Scope-first</option>
                  <option value="event_anchored">Scope + lifecycle event</option>
                  <option value="legacy_event_only">Legacy event only</option>
                </select>
              </label>
            </div>
            <div class="policy-editor-grid">
              <label>Policy scopes
                <span class="option-group" id="policy-evolution-scope-options"></span>
              </label>
              <label>Lifecycle events
                <span class="option-group" id="policy-evolution-lifecycle-options"></span>
              </label>
              <label>Changed path pattern
                <input id="policy-evolution-changed-path" placeholder="Optional scope pattern">
              </label>
            </div>
            <div class="policy-editor-grid">
              <label>Replacement title
                <input id="policy-evolution-replacement-title" placeholder="Required for supersession">
              </label>
              <label>Replacement policy ref
                <input id="policy-evolution-replacement-ref" placeholder="POLICY-new-policy-id">
              </label>
              <span class="subhead policy-editor-note" id="policy-trigger-mode-note">Scope and lifecycle values are selected from the project policy option set.</span>
            </div>
          </div>
        </div>
        <div class="plan-apply-row">
          <div class="policy-action-buttons">
            <button type="button" id="policy-evolution-preview-button">Preview plan</button>
            <button type="button" id="policy-evolution-apply-button" disabled>Apply guarded change</button>
          </div>
          <span id="policy-evolution-apply-note" class="subhead">Preview the configuration change plan to enable guarded apply.</span>
        </div>
        <div class="list" id="policy-evolution-plan-result"></div>
      </div>
      <div class="plan-tool">
        <h3>Make active policy reusable</h3>
        <p class="subhead">Publish a reviewed active policy as a reusable package template for future projects. This does not change the current project's active constraints.</p>
        <div class="policy-detail-grid">
          <div class="policy-detail-panel">
            <h3>Policy to reuse</h3>
            <label>Active project policy
              <select id="policy-template-publication-policy"></select>
            </label>
            <div class="policy-detail-header" id="policy-template-publication-selected-summary"></div>
            <div class="tag-list" id="policy-template-publication-selected-tags"></div>
            <div class="compact-list" id="policy-template-publication-selected-config"></div>
          </div>
          <div class="policy-detail-panel">
            <h3>Reusable template boundary</h3>
            <label>Reuse path
              <select id="policy-template-publication-decision">
                <option value="optional_template">Reusable optional template</option>
                <option value="official_starter">Reusable starter candidate</option>
              </select>
            </label>
            <div class="compact-list">
              <div class="compact-item">
                <strong>Writes after approval</strong>
                <span>one reviewed reusable package policy template file</span>
              </div>
              <div class="compact-item">
                <strong>Non-effect</strong>
                <span>Does not activate, deactivate, or edit current project policies.</span>
              </div>
              <div class="compact-item">
                <strong>Follow-up</strong>
                <span>Starter-pack inclusion remains a separate guarded manifest publication.</span>
              </div>
            </div>
          </div>
        </div>
        <div class="plan-apply-row">
          <div class="policy-action-buttons">
            <button type="button" id="policy-template-publication-preview-button">Preview reusable template</button>
            <button type="button" id="policy-template-publication-apply-button" disabled>Publish reusable template</button>
          </div>
          <span id="policy-template-publication-apply-note" class="subhead">Preview how this active policy becomes a reusable template to enable guarded apply.</span>
        </div>
        <div class="list" id="policy-template-publication-plan-result"></div>
      </div>
      <div class="plan-tool">
        <h3>Template activation preview</h3>
        <p class="subhead">Select a package policy template, inspect the resolved project bindings, then activate it as a project policy through the guarded writer.</p>
        <div class="policy-detail-grid">
          <div class="policy-detail-panel">
            <h3>Selected template</h3>
            <label>Package template
              <select id="policy-template-activation-template"></select>
            </label>
            <div class="policy-detail-header" id="policy-template-selected-summary"></div>
            <div class="tag-list" id="policy-template-selected-tags"></div>
            <div class="compact-list" id="policy-template-selected-config"></div>
          </div>
          <div class="policy-detail-panel">
            <h3>Activation boundary</h3>
            <div class="compact-list">
              <div class="compact-item">
                <strong>Writes after approval</strong>
                <span>proposal snapshot, approved policy, decision record, and manifest ref</span>
              </div>
              <div class="compact-item">
                <strong>Non-effect</strong>
                <span>Does not edit package templates or execute policy actions.</span>
              </div>
              <div class="compact-item">
                <strong>Binding source</strong>
                <span>Resolved from the selected template and .jikuo/project_context.yaml.</span>
              </div>
            </div>
          </div>
        </div>
        <div class="plan-apply-row">
          <div class="policy-action-buttons">
            <button type="button" id="policy-template-activation-preview-button">Preview activation</button>
            <button type="button" id="policy-template-activation-apply-button" disabled>Apply guarded activation</button>
          </div>
          <span id="policy-template-activation-apply-note" class="subhead">Preview a template activation plan to enable guarded apply.</span>
        </div>
        <div class="list" id="policy-template-activation-plan-result"></div>
      </div>
      <div class="panel">
        <h2>Activatable policy proposals</h2>
        <p class="subhead">Only proposal snapshots that can still become active policies are listed here. Review the pending constraint before guarded activation.</p>
        <div class="form-grid">
          <label>
            Pending constraint
            <select id="policy-candidate-activation-proposal"></select>
          </label>
        </div>
        <div class="policy-detail-header" id="policy-candidate-selected-summary"></div>
        <div class="tag-list" id="policy-candidate-selected-tags"></div>
        <div class="compact-list" id="policy-candidate-selected-config"></div>
        <div class="plan-apply-row">
          <div class="policy-action-buttons">
            <button type="button" id="policy-candidate-activation-preview-button">Preview activation</button>
            <button type="button" id="policy-candidate-activation-apply-button" disabled>Apply pending policy</button>
          </div>
          <span id="policy-candidate-activation-apply-note" class="subhead">Preview a pending constraint to enable guarded apply.</span>
        </div>
        <div class="list" id="policy-candidate-activation-plan-result"></div>
      </div>
      <div class="policy-columns policy-primary">
        <div class="policy-column">
          <h3>Active policies</h3>
          <p class="subhead">Current project constraints that can affect AI work.</p>
          <div class="compact-list" id="policy-active-list"></div>
        </div>
        <div class="policy-column">
          <h3>Activatable policies</h3>
          <p class="subhead">Pending constraints that are ready for user review and guarded activation.</p>
          <div class="compact-list" id="policy-candidate-list"></div>
        </div>
      </div>
      <div class="policy-columns" hidden aria-hidden="true">
        <div class="policy-column">
          <h3>Available templates</h3>
          <p class="subhead">Reusable package policy templates and starter-pack inclusion status.</p>
          <div class="compact-list" id="policy-template-list"></div>
        </div>
      </div>
      <div class="policy-columns" hidden aria-hidden="true">
        <div class="policy-column">
          <h3>Starter packs</h3>
          <div class="compact-list" id="policy-starter-pack-list"></div>
        </div>
        <div class="policy-column">
          <h3>Guarded operations</h3>
          <div class="compact-list" id="policy-operation-list"></div>
        </div>
        <div class="policy-column">
          <h3>Read-model limitations</h3>
          <div class="compact-list" id="policy-limitation-list"></div>
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
    const tag = (label, state) => {
      const item = document.createElement("span");
      item.className = `tag ${state || ""}`;
      item.textContent = label;
      return item;
    };
    const policyRecord = (title, detail, status, tags, rows) => {
      const item = document.createElement("div");
      item.className = "policy-record";
      const heading = document.createElement("strong");
      heading.textContent = title || "unnamed policy item";
      const body = document.createElement("p");
      body.textContent = detail || "";
      const badges = document.createElement("div");
      badges.className = "tag-list";
      badges.replaceChildren(...(tags || []));
      const extras = document.createElement("div");
      extras.className = "compact-list";
      extras.replaceChildren(...(rows || []));
      const statusBadge = tag(status || "available", status || "available");
      item.append(heading, body, badges, extras, statusBadge);
      return item;
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
    const POLICY_EVOLUTION_APPROVAL_PHRASE = "Approve Policy Evolution write";
    const POLICY_TEMPLATE_PUBLICATION_APPROVAL_PHRASE = "Approve Policy Template publication";
    const POLICY_TEMPLATE_ACTIVATION_APPROVAL_PHRASE = "Approve Policy Template activation";
    const POLICY_CANDIDATE_ACTIVATION_APPROVAL_PHRASE = "Approve Policy Candidate activation";
    let currentDocumentRulesPlan = null;
    let currentPolicyEvolutionPlan = null;
    let currentPolicyEvolutionRequest = null;
    let currentPolicyTemplatePublicationPlan = null;
    let currentPolicyTemplatePublicationRequest = null;
    let currentPolicyTemplateActivationPlan = null;
    let currentPolicyTemplateActivationRequest = null;
    let currentPolicyCandidateActivationPlan = null;
    let currentPolicyCandidateActivationRequest = null;
    let policyManagementReport = null;
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
    const policyProfileTags = (profile) => {
      if (!profile || typeof profile !== "object") {
        return [tag("work profile not declared", "review")];
      }
      const scopes = profile.policy_scopes || [];
      const events = profile.lifecycle_events || [];
      return [
        ...(scopes.length ? scopes.map((item) => tag(`scope:${item}`, "scope")) : [tag("no policy scopes", "review")]),
        ...(events.length ? events.map((item) => tag(`event:${item}`, "available")) : [tag("scope-first", "available")]),
      ];
    };
    const policyStatusTag = (status) => tag(status || "unknown", (status || "").includes("active") ? "active" : "review");
    const templateStarterTags = (packs) => {
      const records = packs || [];
      return records.length
        ? records.map((item) => tag(`starter:${item.pack_id || "pack"}`, "available"))
        : [tag("not in starter pack", "review")];
    };
    const stringValues = (items) => (items || []).map((item) => String(item)).filter((item) => item);
    const listSummary = (items, fallback) => {
      const values = stringValues(items);
      return values.length ? values.join(", ") : fallback;
    };
    const distributionByPolicyId = (report) => {
      const entries = (report.active_policy_distribution || []).map((item) => [item.policy_id, item]);
      return Object.fromEntries(entries.filter(([key]) => key));
    };
    const activePolicyDetails = (report) => ((report.policy_store || {}).active_policy_details || []);
    const activePolicyDetailById = (report) => Object.fromEntries(
      activePolicyDetails(report).map((item) => [item.policy_id, item]).filter(([key]) => key)
    );
    const activatablePolicyProposals = (report) => ((report.policy_store || {}).activatable_policy_proposals || []);
    const shortRecordList = (items, fallback) => {
      const values = (items || []).map((item) => {
        if (!item || typeof item !== "object") return "";
        return item.type || item.action_id || item.evidence_id || item.policy_id || "";
      }).filter((item) => item);
      return values.length ? values.join(", ") : fallback;
    };
    const selectedActivePolicyDetail = (report, selectId) => {
      const policyRef = document.getElementById(selectId).value;
      return activePolicyDetailById(report || policyManagementReport || {})[policyRef] || null;
    };
    const selectedPolicyDetail = (report) => selectedActivePolicyDetail(report, "policy-evolution-policy");
    const selectedPublicationPolicyDetail = (report) => selectedActivePolicyDetail(report, "policy-template-publication-policy");
    const proposalDetailsById = (report) => {
      const output = {};
      activatablePolicyProposals(report || {}).forEach((item) => {
        if (item.proposal_id) output[item.proposal_id] = item;
        if (item.proposal_ref) output[item.proposal_ref] = item;
        if (item.path) output[item.path] = item;
      });
      return output;
    };
    const selectedCandidateProposalDetail = (report) => {
      const select = document.getElementById("policy-candidate-activation-proposal");
      const proposalId = select.value;
      if (!proposalId) return null;
      const details = proposalDetailsById(report || policyManagementReport || {});
      return details[proposalId] || null;
    };
    const policyCandidateActivationRequestFromSelection = () => {
      const detail = selectedCandidateProposalDetail(policyManagementReport || {});
      const select = document.getElementById("policy-candidate-activation-proposal");
      return {
        proposal_id: (detail || {}).proposal_id || select.value || null,
        proposal_ref: (detail || {}).proposal_ref || (detail || {}).path || null,
      };
    };
    const optionSetValues = (report, key, fallback) => {
      const values = (((report || {}).option_sets || {})[key] || []).map((item) => String(item)).filter((item) => item);
      return values.length ? values : fallback;
    };
    const renderOptionGroup = (containerId, name, options, selected) => {
      const container = document.getElementById(containerId);
      const selectedSet = new Set(stringValues(selected));
      const fields = options.map((option) => {
        const label = document.createElement("label");
        label.className = "option-pill";
        const input = document.createElement("input");
        input.type = "checkbox";
        input.name = name;
        input.value = option;
        input.checked = selectedSet.has(option);
        const textNode = document.createTextNode(option);
        label.append(input, textNode);
        return label;
      });
      container.replaceChildren(...(fields.length ? fields : [tag("no options", "review")]));
    };
    const selectedOptionValues = (name) => Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map((item) => item.value);
    const selectedPolicyTriggerProfile = () => {
      const detail = selectedPolicyDetail(policyManagementReport || {});
      return (detail || {}).trigger_profile || {};
    };
    const setOptionGroupIgnored = (containerId, ignored) => {
      document.querySelectorAll(`#${containerId} .option-pill`).forEach((label) => {
        label.classList.toggle("ignored", ignored);
        const input = label.querySelector("input");
        if (input) {
          input.disabled = ignored;
        }
      });
    };
    const updatePolicyTriggerModeAffordance = () => {
      const mode = document.getElementById("policy-evolution-trigger-mode").value;
      setOptionGroupIgnored("policy-evolution-scope-options", mode === "legacy_event_only");
      setOptionGroupIgnored("policy-evolution-lifecycle-options", mode === "scope_first");
      const note = document.getElementById("policy-trigger-mode-note");
      if (mode === "scope_first") {
        note.textContent = "Scope-first uses policy scopes for applicability; lifecycle events are ignored and the current declared trigger is kept as a compatibility anchor.";
      } else if (mode === "legacy_event_only") {
        note.textContent = "Legacy event only ignores policy scopes; choose one lifecycle event as the event anchor.";
      } else {
        note.textContent = "Scope + lifecycle event requires both selected scopes and selected lifecycle events to match.";
      }
    };
    const policyEvolutionApplyReady = (plan) => {
      const candidate = plan || currentPolicyEvolutionPlan || {};
      const boundary = candidate.future_write_boundary || {};
      return Boolean(
        candidate.status === "review"
        && boundary.writer_implemented
        && (candidate.write_set || []).length
        && !(candidate.refusal_reasons || []).length
      );
    };
    const updatePolicyEvolutionApplyButton = () => {
      const button = document.getElementById("policy-evolution-apply-button");
      const note = document.getElementById("policy-evolution-apply-note");
      const plan = currentPolicyEvolutionPlan || {};
      const ready = policyEvolutionApplyReady(plan);
      const boundary = plan.future_write_boundary || {};
      button.disabled = !ready;
      button.textContent = "Apply guarded change";
      if (ready) {
        note.textContent = `Confirmation required before writing ${numberValue((plan.write_set || []).length)} policy-store item(s).`;
      } else if (currentPolicyEvolutionPlan && !boundary.writer_implemented) {
        note.textContent = "This operation has no Studio/Core guarded writer yet; preview remains no-write.";
      } else if (currentPolicyEvolutionPlan && (plan.status || "") !== "review") {
        note.textContent = "Resolve plan refusal reasons before guarded apply.";
      } else {
        note.textContent = "Preview the configuration change plan to enable guarded apply.";
      }
    };
    const invalidatePolicyEvolutionPlan = () => {
      currentPolicyEvolutionPlan = null;
      currentPolicyEvolutionRequest = null;
      const container = document.getElementById("policy-evolution-plan-result");
      if (container.childElementCount) {
        container.replaceChildren(row("Preview required", "Policy fields changed after the last preview.", "degraded"));
      }
      updatePolicyEvolutionApplyButton();
    };
    const triggerModeFromProfile = (profile) => {
      if (!profile || typeof profile !== "object") {
        return "scope_first";
      }
      if (profile.trigger_mode) {
        return profile.trigger_mode;
      }
      const scopes = stringValues(profile.policy_scopes || ((profile.work_profile || {}).policy_scopes));
      const events = stringValues(profile.lifecycle_events || ((profile.work_profile || {}).lifecycle_events));
      const declared = stringValues(profile.declared_trigger_events || (profile.declared_trigger_event ? [profile.declared_trigger_event] : []));
      if (scopes.length && !events.length) {
        return "scope_first";
      }
      if (scopes.length && events.length) {
        return "event_anchored";
      }
      return declared.length ? "legacy_event_only" : "scope_first";
    };
    const triggerProfileDetailText = (profile) => {
      if (!profile || typeof profile !== "object") {
        return "Trigger profile not declared.";
      }
      const workProfile = profile.work_profile || profile.work_profile_applicability || profile;
      const scopes = stringValues(profile.policy_scopes || workProfile.policy_scopes);
      const events = stringValues(profile.lifecycle_events || workProfile.lifecycle_events);
      const declared = stringValues(profile.declared_trigger_events || (profile.declared_trigger_event ? [profile.declared_trigger_event] : []));
      return [
        `mode: ${triggerModeFromProfile(profile)}`,
        `scopes: ${listSummary(scopes, "none")}`,
        `events: ${listSummary(events, "none")}`,
        `declared: ${listSummary(declared, "none")}`,
      ].join(" / ");
    };
    const populatePolicyTriggerOptions = (report, detail) => {
      const profile = (detail || {}).trigger_profile || {};
      const scopes = stringValues(profile.policy_scopes);
      const events = stringValues(profile.lifecycle_events);
      const mode = triggerModeFromProfile(profile);
      const triggerMode = document.getElementById("policy-evolution-trigger-mode");
      triggerMode.value = optionSetValues(report, "trigger_modes", ["scope_first", "event_anchored", "legacy_event_only"]).includes(mode)
        ? mode
        : "scope_first";
      renderOptionGroup(
        "policy-evolution-scope-options",
        "policy_evolution_scope",
        optionSetValues(report, "policy_scopes", ["discussion", "editing", "progress_summary"]),
        scopes
      );
      renderOptionGroup(
        "policy-evolution-lifecycle-options",
        "policy_evolution_lifecycle",
        optionSetValues(report, "lifecycle_events", ["conversation_turn", "task_start", "completion_review"]),
        events
      );
      updatePolicyTriggerModeAffordance();
    };
    const renderSelectedPolicyDetail = (report) => {
      const detail = selectedPolicyDetail(report);
      const summary = document.getElementById("policy-selected-summary");
      const triggerTags = document.getElementById("policy-selected-trigger-tags");
      const config = document.getElementById("policy-selected-config");
      if (!detail) {
        summary.replaceChildren(compactItem("No policy selected", "Select an active policy to inspect its current configuration."));
        triggerTags.replaceChildren(tag("no selection", "review"));
        config.replaceChildren(compactItem("No current configuration", "Policy detail is unavailable in the read model."));
        populatePolicyTriggerOptions(report, null);
        return;
      }
      const header = document.createElement("div");
      header.innerHTML = `<strong></strong><span></span>`;
      header.querySelector("strong").textContent = detail.title || detail.policy_id || "Untitled policy";
      header.querySelector("span").textContent = `${detail.policy_id || "policy id missing"} / ${detail.status || "status unknown"} / ${detail.path || "path not supplied"}`;
      summary.replaceChildren(header);
      const profile = detail.trigger_profile || {};
      triggerTags.replaceChildren(...policyProfileTags(profile));
      const filters = detail.condition_filters || {};
      const actions = detail.required_actions || [];
      const evidence = detail.required_evidence || [];
      config.replaceChildren(
        compactItem("Trigger profile", triggerProfileDetailText(profile)),
        compactItem("Task types", listSummary(filters.task_types, "No task-type filter")),
        compactItem("JIKUO layers", listSummary(filters.jikuo_layers, "No layer filter")),
        compactItem("Path filters", [
          `changed: ${listSummary(filters.changed_path_patterns, "none")}`,
          `added: ${listSummary(filters.added_path_patterns, "none")}`,
        ].join(" / ")),
        compactItem("Required actions", actions.length ? actions.map((item) => item.type || item.action_id || "action").join(", ") : "No required actions declared"),
        compactItem("Required evidence", evidence.length ? evidence.map((item) => item.type || item.evidence_id || "evidence").join(", ") : "No required evidence declared")
      );
      populatePolicyTriggerOptions(report, detail);
    };
    const populatePolicyEvolutionTargets = (report) => {
      const select = document.getElementById("policy-evolution-policy");
      const active = (report.policy_store || {}).active_policies || [];
      const previousValue = select.value;
      const options = active.map((item) => {
        const option = document.createElement("option");
        option.value = item.policy_id || "";
        option.textContent = `${item.policy_id || "policy"}${item.title ? ` / ${item.title}` : ""}`;
        return option;
      }).filter((option) => option.value);
      select.replaceChildren(...options);
      if (!options.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No active policies";
        select.replaceChildren(option);
      }
      if (previousValue && options.some((option) => option.value === previousValue)) {
        select.value = previousValue;
      }
      renderSelectedPolicyDetail(report);
    };
    const renderSelectedPublicationPolicyDetail = (report) => {
      const detail = selectedPublicationPolicyDetail(report);
      const summary = document.getElementById("policy-template-publication-selected-summary");
      const triggerTags = document.getElementById("policy-template-publication-selected-tags");
      const config = document.getElementById("policy-template-publication-selected-config");
      const distribution = distributionByPolicyId(report || policyManagementReport || {});
      if (!detail) {
        summary.replaceChildren(compactItem("No policy selected", "Select an active policy to package as a reusable template."));
        triggerTags.replaceChildren(tag("no selection", "review"));
        config.replaceChildren(compactItem("No current configuration", "Policy detail is unavailable in the read model."));
        return;
      }
      const dist = distribution[detail.policy_id] || {};
      const header = document.createElement("div");
      header.innerHTML = `<strong></strong><span></span>`;
      header.querySelector("strong").textContent = detail.title || detail.policy_id || "Untitled policy";
      header.querySelector("span").textContent = `${detail.policy_id || "policy id missing"} / ${detail.status || "status unknown"} / ${detail.path || "path not supplied"}`;
      summary.replaceChildren(header);
      triggerTags.replaceChildren(
        tag(dist.distribution_state || "distribution unknown", dist.distribution_state === "active_project_policy_only" ? "review" : "available"),
        ...policyProfileTags(detail.trigger_profile)
      );
      const filters = detail.condition_filters || {};
      const actions = detail.required_actions || [];
      const evidence = detail.required_evidence || [];
      config.replaceChildren(
        compactItem("Trigger profile", triggerProfileDetailText(detail.trigger_profile)),
        compactItem("Existing template refs", (dist.package_template_refs || []).join(", ") || "No reusable template ref"),
        compactItem("Path filters", [
          `changed: ${listSummary(filters.changed_path_patterns, "none")}`,
          `added: ${listSummary(filters.added_path_patterns, "none")}`,
        ].join(" / ")),
        compactItem("Required actions", actions.length ? actions.map((item) => item.type || item.action_id || "action").join(", ") : "No required actions declared"),
        compactItem("Required evidence", evidence.length ? evidence.map((item) => item.type || item.evidence_id || "evidence").join(", ") : "No required evidence declared")
      );
    };
    const populatePolicyTemplatePublicationTargets = (report) => {
      const select = document.getElementById("policy-template-publication-policy");
      const active = (report.policy_store || {}).active_policies || [];
      const previousValue = select.value;
      const options = active.map((item) => {
        const option = document.createElement("option");
        option.value = item.policy_id || "";
        option.textContent = `${item.policy_id || "policy"}${item.title ? ` / ${item.title}` : ""}`;
        return option;
      }).filter((option) => option.value);
      select.replaceChildren(...options);
      if (!options.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No active policies";
        select.replaceChildren(option);
      }
      if (previousValue && options.some((option) => option.value === previousValue)) {
        select.value = previousValue;
      }
      renderSelectedPublicationPolicyDetail(report);
    };
    const policyTemplatePublicationRequest = () => {
      const detail = selectedPublicationPolicyDetail(policyManagementReport || {});
      const decision = document.getElementById("policy-template-publication-decision").value;
      return {
        policy_ref: (detail || {}).policy_id || document.getElementById("policy-template-publication-policy").value || null,
        source_policy_path: (detail || {}).path || null,
        distribution_decision: decision || "optional_template",
        namespace: "local",
        rationale: "Studio active-policy reusable-template publication preview",
      };
    };
    const policyTemplatePublicationApplyReady = (plan) => {
      const candidate = plan || currentPolicyTemplatePublicationPlan || {};
      return Boolean(
        candidate.status === "review"
        && (candidate.write_set || []).length
        && !(candidate.refusal_reasons || []).length
      );
    };
    const updatePolicyTemplatePublicationApplyButton = () => {
      const button = document.getElementById("policy-template-publication-apply-button");
      const note = document.getElementById("policy-template-publication-apply-note");
      const plan = currentPolicyTemplatePublicationPlan || {};
      const ready = policyTemplatePublicationApplyReady(plan);
      button.disabled = !ready;
      button.textContent = "Publish reusable template";
      if (ready) {
        note.textContent = `Confirmation required before writing ${numberValue((plan.write_set || []).length)} reusable-template file(s).`;
      } else if (currentPolicyTemplatePublicationPlan && (plan.status || "") !== "review") {
        note.textContent = "Resolve reusable-template refusal reasons before guarded apply.";
      } else {
        note.textContent = "Preview how this active policy becomes a reusable template to enable guarded apply.";
      }
    };
    const invalidatePolicyTemplatePublicationPlan = () => {
      currentPolicyTemplatePublicationPlan = null;
      currentPolicyTemplatePublicationRequest = null;
      const container = document.getElementById("policy-template-publication-plan-result");
      if (container.childElementCount) {
        container.replaceChildren(row("Preview required", "Reusable-template fields changed after the last preview.", "degraded"));
      }
      updatePolicyTemplatePublicationApplyButton();
    };
    const renderPolicyTemplatePublicationPlan = (plan) => {
      const container = document.getElementById("policy-template-publication-plan-result");
      const status = plan.status || "unknown";
      const summaryStatus = status === "review" ? "degraded" : (status === "refused" ? "unavailable" : "available");
      const writeSet = (plan.write_set || []).map((item) =>
        compactItem(item.effect || "write", item.path || "path not supplied")
      );
      const refusals = (plan.refusal_reasons || []).map((item) => compactItem("Refusal", item));
      const warnings = (plan.warnings || []).map((item) => compactItem("Warning", item));
      const nonEffects = (plan.non_effects || []).slice(0, 4).map((item) => compactItem("Non-effect", item));
      const nextActions = (plan.next_actions || []).map((item) => compactItem("Next", item));
      container.replaceChildren(
        row(`Plan ${status}`, `reusable-template publication / writes performed: ${String(Boolean(plan.writes_performed))}`, summaryStatus),
        compactItem("Source policy", `${plan.policy_id || "policy id missing"} / ${plan.title || "title not supplied"}`),
        compactItem("Reuse path", plan.distribution_decision || "decision not supplied"),
        compactItem("Reusable template ref", plan.target_template_ref || "template ref not supplied"),
        compactItem("Reusable template path", plan.target_template_path || "target path not supplied"),
        compactItem("Starter manifest", `${plan.starter_pack_manifest_change_required ? "follow-up required" : "not required"} / ${plan.starter_pack_manifest_change_status || "unknown"}`),
        ...(writeSet.length ? writeSet : [compactItem("Write set", "No reusable-template writes projected.")]),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(nextActions.length ? nextActions : []),
        ...(nonEffects.length ? nonEffects : [])
      );
      updatePolicyTemplatePublicationApplyButton();
    };
    const renderPolicyTemplatePublicationApplyResult = (result) => {
      const container = document.getElementById("policy-template-publication-plan-result");
      const status = result.status || "unknown";
      const summaryStatus = status === "written" ? "available" : "unavailable";
      const writtenPaths = (result.written_paths || []).map((item) => compactItem("Written path", item));
      const createdPaths = (result.created_paths || []).map((item) => compactItem("Created path", item));
      const refusals = (result.refusal_reasons || []).map((item) => compactItem("Refusal", item));
      const warnings = (result.warnings || []).map((item) => compactItem("Warning", item));
      const nextActions = (result.next_actions || []).map((item) => compactItem("Next", item));
      container.replaceChildren(
        row(`Apply ${status}`, `reusable-template publication / write performed: ${String(Boolean(result.write_performed))}`, summaryStatus),
        compactItem("Template ref", result.template_ref || "template ref not supplied"),
        compactItem("Reusable template path", result.target_template_path || "target path not supplied"),
        compactItem("Source policy", result.source_policy_path || "source policy not supplied"),
        compactItem("Starter manifest", `${result.starter_pack_manifest_change_required ? "follow-up required" : "not required"} / ${result.starter_pack_manifest_change_status || "unknown"}`),
        ...(writtenPaths.length ? writtenPaths : [compactItem("Written paths", "No reusable-template writes were reported.")]),
        ...(createdPaths.length ? createdPaths : []),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(nextActions.length ? nextActions : [])
      );
      if (status === "written") {
        currentPolicyTemplatePublicationPlan = null;
        currentPolicyTemplatePublicationRequest = null;
        updatePolicyTemplatePublicationApplyButton();
        fetch("/api/status", {cache: "no-store"}).then((response) => response.json()).then(render);
      }
    };
    const previewPolicyTemplatePublicationPlan = () => {
      const button = document.getElementById("policy-template-publication-preview-button");
      const container = document.getElementById("policy-template-publication-plan-result");
      const requestPayload = policyTemplatePublicationRequest();
      currentPolicyTemplatePublicationPlan = null;
      currentPolicyTemplatePublicationRequest = null;
      updatePolicyTemplatePublicationApplyButton();
      button.disabled = true;
      button.textContent = "Previewing";
      container.replaceChildren(row("Previewing reusable template", "Building no-write reusable-template publication plan.", "degraded"));
      fetch("/api/policy-management/template-publication/plan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(requestPayload),
      })
        .then((response) => response.json())
        .then((plan) => {
          currentPolicyTemplatePublicationPlan = plan;
          currentPolicyTemplatePublicationRequest = requestPayload;
          renderPolicyTemplatePublicationPlan(plan);
        })
        .catch((error) => container.replaceChildren(row("Preview failed", error.message, "unavailable")))
        .finally(() => {
          button.disabled = false;
          button.textContent = "Preview reusable template";
          updatePolicyTemplatePublicationApplyButton();
        });
    };
    const applyPolicyTemplatePublicationPlan = () => {
      const button = document.getElementById("policy-template-publication-apply-button");
      const container = document.getElementById("policy-template-publication-plan-result");
      if (!currentPolicyTemplatePublicationPlan || !currentPolicyTemplatePublicationRequest || !policyTemplatePublicationApplyReady(currentPolicyTemplatePublicationPlan)) {
        container.replaceChildren(row("Plan required", "Preview and review a reusable-template publication plan before applying.", "unavailable"));
        updatePolicyTemplatePublicationApplyButton();
        return;
      }
      const writeCount = (currentPolicyTemplatePublicationPlan.write_set || []).length;
      const confirmed = window.confirm(
        `Publish this active policy as a reusable template?\n\nPolicy: ${currentPolicyTemplatePublicationPlan.policy_id || "policy"}\nReuse path: ${currentPolicyTemplatePublicationPlan.distribution_decision || "decision"}\nReusable-template files to write: ${writeCount}\n\nThis writes a reviewed package policy template through the guarded writer. It does not activate, deactivate, or edit current project policies, and it does not update starter-pack manifests.`
      );
      if (!confirmed) {
        return;
      }
      button.disabled = true;
      button.textContent = "Publishing";
      fetch("/api/policy-management/template-publication/apply", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...currentPolicyTemplatePublicationRequest,
          reviewed_source_policy_sha256: currentPolicyTemplatePublicationPlan.source_policy_sha256 || null,
          reviewed_target_template_path: currentPolicyTemplatePublicationPlan.target_template_path || null,
          confirm_apply: true,
          approval_phrase: POLICY_TEMPLATE_PUBLICATION_APPROVAL_PHRASE,
          approval_source: "studio_confirmation_dialog",
        }),
      })
        .then((response) => response.json())
        .then(renderPolicyTemplatePublicationApplyResult)
        .catch((error) => container.replaceChildren(row("Apply failed", error.message, "unavailable")))
        .finally(() => {
          button.textContent = "Publish reusable template";
          updatePolicyTemplatePublicationApplyButton();
        });
    };
    const packageTemplates = (report) => ((report.package_templates || {}).templates || []);
    const selectedTemplateRecord = (report) => {
      const templateRef = document.getElementById("policy-template-activation-template").value;
      return packageTemplates(report || policyManagementReport || {}).find((item) =>
        (item.template_ref || item.template_path || item.template_id) === templateRef
      ) || null;
    };
    const renderSelectedTemplateDetail = (report) => {
      const detail = selectedTemplateRecord(report);
      const summary = document.getElementById("policy-template-selected-summary");
      const tags = document.getElementById("policy-template-selected-tags");
      const config = document.getElementById("policy-template-selected-config");
      if (!detail) {
        summary.replaceChildren(compactItem("No template selected", "Select a package template to preview activation."));
        tags.replaceChildren(tag("no selection", "review"));
        config.replaceChildren(compactItem("No template configuration", "Template detail is unavailable in the read model."));
        return;
      }
      const header = document.createElement("div");
      header.innerHTML = `<strong></strong><span></span>`;
      header.querySelector("strong").textContent = detail.title || detail.template_policy_title || detail.template_id || "Untitled template";
      header.querySelector("span").textContent = `${detail.template_policy_id || "policy id missing"} / ${detail.template_ref || "template ref not supplied"}`;
      summary.replaceChildren(header);
      tags.replaceChildren(
        tag(detail.namespace || "namespace", "available"),
        tag(`v${detail.version || "?"}`, "available"),
        tag(`${detail.required_binding_count || 0} bindings`, detail.required_binding_count ? "review" : "available"),
        ...templateStarterTags(detail.included_in_starter_packs)
      );
      config.replaceChildren(
        compactItem("Template policy", `${detail.template_policy_id || "policy id missing"} / ${detail.template_policy_title || "title not supplied"}`),
        compactItem("Template file", detail.template_path || detail.template_ref || "template path not supplied"),
        compactItem("Portability", detail.portability_status || "portability not reported"),
        compactItem("Starter packs", (detail.included_in_starter_packs || []).map((pack) => pack.pack_id).join(", ") || "No starter pack ref")
      );
    };
    const populatePolicyTemplateActivationTargets = (report) => {
      const select = document.getElementById("policy-template-activation-template");
      const previousValue = select.value;
      const options = packageTemplates(report).map((item) => {
        const option = document.createElement("option");
        option.value = item.template_ref || item.template_path || item.template_id || "";
        option.textContent = `${item.template_policy_id || item.template_id || "template"}${item.title ? ` / ${item.title}` : ""}`;
        option.dataset.templatePath = item.template_path || "";
        option.dataset.templateRef = item.template_ref || "";
        return option;
      }).filter((option) => option.value);
      select.replaceChildren(...options);
      if (!options.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No package templates";
        select.replaceChildren(option);
      }
      if (previousValue && options.some((option) => option.value === previousValue)) {
        select.value = previousValue;
      }
      renderSelectedTemplateDetail(report);
    };
    const policyTemplateActivationRequest = () => {
      const detail = selectedTemplateRecord(policyManagementReport || {});
      return {
        template_ref: (detail || {}).template_ref || document.getElementById("policy-template-activation-template").value || null,
        template_path: (detail || {}).template_path || null,
      };
    };
    const policyTemplateActivationApplyReady = (plan) => {
      const candidate = plan || currentPolicyTemplateActivationPlan || {};
      return Boolean(
        candidate.status === "review"
        && (candidate.write_set || []).length
        && !(candidate.refusal_reasons || []).length
      );
    };
    const updatePolicyTemplateActivationApplyButton = () => {
      const button = document.getElementById("policy-template-activation-apply-button");
      const note = document.getElementById("policy-template-activation-apply-note");
      const plan = currentPolicyTemplateActivationPlan || {};
      const ready = policyTemplateActivationApplyReady(plan);
      button.disabled = !ready;
      button.textContent = "Apply guarded activation";
      if (ready) {
        note.textContent = `Confirmation required before writing ${numberValue((plan.write_set || []).length)} policy-store item(s).`;
      } else if (currentPolicyTemplateActivationPlan && (plan.status || "") !== "review") {
        note.textContent = "Resolve template binding or plan refusal reasons before guarded activation.";
      } else {
        note.textContent = "Preview a template activation plan to enable guarded apply.";
      }
    };
    const invalidatePolicyTemplateActivationPlan = () => {
      currentPolicyTemplateActivationPlan = null;
      currentPolicyTemplateActivationRequest = null;
      const container = document.getElementById("policy-template-activation-plan-result");
      if (container.childElementCount) {
        container.replaceChildren(row("Preview required", "Template selection changed after the last preview.", "degraded"));
      }
      updatePolicyTemplateActivationApplyButton();
    };
    const renderPolicyTemplateActivationPlan = (plan) => {
      const container = document.getElementById("policy-template-activation-plan-result");
      const status = plan.status || "unknown";
      const summaryStatus = status === "review" ? "degraded" : (status === "refused" ? "unavailable" : "available");
      const resolved = plan.resolved_policy_preview || {};
      const bindings = (plan.binding_status || []).map((item) =>
        compactItem(
          item.binding_id || item.role_ref || "binding",
          `${item.status || "unknown"} / ${item.role_ref || "role not supplied"} -> ${item.resolved_ref || item.reason || "not resolved"}`
        )
      );
      const writeSet = (plan.write_set || []).map((item) =>
        compactItem(item.operation || "write", `${item.path || "path not supplied"} / ${item.effect || "effect not supplied"}`)
      );
      const refusals = (plan.refusal_reasons || []).map((item) => compactItem("Refusal", item));
      const warnings = (plan.warnings || []).map((item) => compactItem("Warning", item));
      const nonEffects = (plan.non_effects || []).slice(0, 4).map((item) => compactItem("Non-effect", item));
      const nextActions = (plan.next_actions || []).map((item) => compactItem("Next", item));
      container.replaceChildren(
        row(`Plan ${status}`, `template activation / writes performed: ${String(Boolean(plan.writes_performed))}`, summaryStatus),
        compactItem("Resolved policy", `${resolved.policy_id || "policy id missing"} / ${resolved.title || "title not supplied"}`),
        compactItem("Template ref", plan.template_ref || "template ref not supplied"),
        compactItem("Project context", `${plan.project_context_ref || ".jikuo/project_context.yaml"} / ${plan.project_context_status || "unknown"}`),
        compactItem("Proposal ref", plan.proposal_ref || "proposal ref not supplied"),
        compactItem("Decision record", plan.decision_record_ref || "decision record not supplied"),
        ...(bindings.length ? bindings : [compactItem("Bindings", "No required bindings declared.")]),
        ...(writeSet.length ? writeSet : [compactItem("Write set", "No future writes projected.")]),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(nextActions.length ? nextActions : []),
        ...(nonEffects.length ? nonEffects : [])
      );
      updatePolicyTemplateActivationApplyButton();
    };
    const renderPolicyTemplateActivationApplyResult = (result) => {
      const container = document.getElementById("policy-template-activation-plan-result");
      const status = result.status || "unknown";
      const summaryStatus = status === "written" ? "available" : "unavailable";
      const writtenPaths = (result.written_paths || []).map((item) => compactItem("Written path", item));
      const createdPaths = (result.created_paths || []).map((item) => compactItem("Created path", item));
      const refusals = (result.refusal_reasons || []).map((item) => compactItem("Refusal", item));
      const warnings = (result.warnings || []).map((item) => compactItem("Warning", item));
      const nextActions = (result.next_actions || []).map((item) => compactItem("Next", item));
      const verification = result.post_write_verification || {};
      container.replaceChildren(
        row(`Apply ${status}`, `template activation / write performed: ${String(Boolean(result.write_performed))}`, summaryStatus),
        compactItem("Activated policy", result.policy_ref || "policy ref not supplied"),
        compactItem("Template ref", result.template_ref || "template ref not supplied"),
        compactItem("Proposal ref", result.proposal_ref || "proposal ref not supplied"),
        compactItem("Decision record", result.decision_record_ref || "decision record not supplied"),
        compactItem("Verification", `active: ${String(Boolean(verification.policy_active))} / store: ${verification.policy_store_status || "unknown"}`),
        ...(writtenPaths.length ? writtenPaths : [compactItem("Written paths", "No policy-store writes were reported.")]),
        ...(createdPaths.length ? createdPaths : []),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(nextActions.length ? nextActions : [])
      );
      if (status === "written") {
        currentPolicyTemplateActivationPlan = null;
        currentPolicyTemplateActivationRequest = null;
        updatePolicyTemplateActivationApplyButton();
        fetch("/api/status", {cache: "no-store"}).then((response) => response.json()).then(render);
      }
    };
    const previewPolicyTemplateActivationPlan = () => {
      const button = document.getElementById("policy-template-activation-preview-button");
      const container = document.getElementById("policy-template-activation-plan-result");
      const requestPayload = policyTemplateActivationRequest();
      currentPolicyTemplateActivationPlan = null;
      currentPolicyTemplateActivationRequest = null;
      updatePolicyTemplateActivationApplyButton();
      button.disabled = true;
      button.textContent = "Previewing";
      container.replaceChildren(row("Previewing activation", "Building no-write template activation plan.", "degraded"));
      fetch("/api/policy-management/template-activation/plan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(requestPayload),
      })
        .then((response) => response.json())
        .then((plan) => {
          currentPolicyTemplateActivationPlan = plan;
          currentPolicyTemplateActivationRequest = requestPayload;
          renderPolicyTemplateActivationPlan(plan);
        })
        .catch((error) => container.replaceChildren(row("Preview failed", error.message, "unavailable")))
        .finally(() => {
          button.disabled = false;
          button.textContent = "Preview activation";
          updatePolicyTemplateActivationApplyButton();
        });
    };
    const applyPolicyTemplateActivationPlan = () => {
      const button = document.getElementById("policy-template-activation-apply-button");
      const container = document.getElementById("policy-template-activation-plan-result");
      if (!currentPolicyTemplateActivationPlan || !currentPolicyTemplateActivationRequest || !policyTemplateActivationApplyReady(currentPolicyTemplateActivationPlan)) {
        container.replaceChildren(row("Plan required", "Preview and review a resolved template activation plan before applying.", "unavailable"));
        updatePolicyTemplateActivationApplyButton();
        return;
      }
      const resolved = currentPolicyTemplateActivationPlan.resolved_policy_preview || {};
      const writeCount = (currentPolicyTemplateActivationPlan.write_set || []).length;
      const confirmed = window.confirm(
        `Activate this policy template?\n\nPolicy: ${resolved.policy_id || "policy"}\nTemplate: ${currentPolicyTemplateActivationPlan.template_ref || "template"}\nPolicy-store records/files to write: ${writeCount}\n\nThis persists a proposal snapshot, approved policy, decision record, and manifest ref through the guarded writer. It does not execute policy actions.`
      );
      if (!confirmed) {
        return;
      }
      button.disabled = true;
      button.textContent = "Applying";
      fetch("/api/policy-management/template-activation/apply", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...currentPolicyTemplateActivationRequest,
          plan_id: currentPolicyTemplateActivationPlan.plan_id || null,
          confirm_apply: true,
          approval_phrase: POLICY_TEMPLATE_ACTIVATION_APPROVAL_PHRASE,
          approval_source: "studio_confirmation_dialog",
        }),
      })
        .then((response) => response.json())
        .then(renderPolicyTemplateActivationApplyResult)
        .catch((error) => container.replaceChildren(row("Apply failed", error.message, "unavailable")))
        .finally(() => {
          button.textContent = "Apply guarded activation";
          updatePolicyTemplateActivationApplyButton();
        });
    };
    const renderSelectedCandidateProposalDetail = (report) => {
      const detail = selectedCandidateProposalDetail(report);
      const summary = document.getElementById("policy-candidate-selected-summary");
      const tags = document.getElementById("policy-candidate-selected-tags");
      const config = document.getElementById("policy-candidate-selected-config");
      if (!detail) {
        summary.replaceChildren(compactItem("No activatable policy selected", "Select a pending constraint to preview activation."));
        tags.replaceChildren(tag("no selection", "review"));
        config.replaceChildren(compactItem("No pending constraint", "No activatable policy proposal is available in the read model."));
        return;
      }
      const header = document.createElement("div");
      header.innerHTML = `<strong></strong><span></span>`;
      header.querySelector("strong").textContent = detail.title || detail.policy_id || detail.proposal_id || "Untitled policy proposal";
      header.querySelector("span").textContent = `${detail.proposal_id || "proposal id missing"} / ${detail.path || "path not supplied"}`;
      summary.replaceChildren(header);
      tags.replaceChildren(
        tag(detail.activation_status || "ready_to_activate", "available"),
        tag(detail.status || "review", detail.status || "review"),
        tag(detail.manifest_status || "manifest status", "review"),
        ...policyProfileTags(detail.trigger_profile || {})
      );
      config.replaceChildren(
        compactItem("Target policy", detail.policy_id || "policy id missing"),
        compactItem("Pending constraint", triggerProfileDetailText(detail.trigger_profile || {})),
        compactItem("Required actions if activated", shortRecordList(detail.required_actions, "No required actions declared.")),
        compactItem("Required evidence if activated", shortRecordList(detail.required_evidence, "No required evidence declared.")),
        compactItem("Guarded write", `${detail.write_set_count || 0} policy-store item(s) after approval.`)
      );
    };
    const populatePolicyCandidateActivationTargets = (report) => {
      const select = document.getElementById("policy-candidate-activation-proposal");
      const previousValue = select.value;
      const details = activatablePolicyProposals(report || {}).filter((item) => item.proposal_id || item.path || item.proposal_ref);
      const options = details.map((item) => {
        const option = document.createElement("option");
        option.value = item.proposal_id || item.path || item.proposal_ref || "";
        option.textContent = `${item.policy_id || item.proposal_id || "policy"}${item.title ? ` / ${item.title}` : ""}`;
        option.dataset.proposalRef = item.proposal_ref || item.path || "";
        option.dataset.proposalId = item.proposal_id || "";
        return option;
      }).filter((option) => option.value);
      select.replaceChildren(...options);
      if (!options.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No activatable policies";
        select.replaceChildren(option);
      }
      if (previousValue && options.some((option) => option.value === previousValue)) {
        select.value = previousValue;
      }
      renderSelectedCandidateProposalDetail(report);
    };
    const policyCandidateActivationApplyReady = (plan) => {
      const candidate = plan || currentPolicyCandidateActivationPlan || {};
      return Boolean(
        candidate.status === "review"
        && (candidate.write_set || []).length
        && !(candidate.refusal_reasons || []).length
        && candidate.guarded_apply_available
      );
    };
    const updatePolicyCandidateActivationApplyButton = () => {
      const button = document.getElementById("policy-candidate-activation-apply-button");
      const note = document.getElementById("policy-candidate-activation-apply-note");
      const plan = currentPolicyCandidateActivationPlan || {};
      const ready = policyCandidateActivationApplyReady(plan);
      button.disabled = !ready;
      button.textContent = "Apply pending policy";
      if (ready) {
        note.textContent = `Confirmation required before writing ${numberValue((plan.write_set || []).length)} policy-store item(s).`;
      } else if (currentPolicyCandidateActivationPlan && (plan.refusal_reasons || []).length) {
        note.textContent = "This proposal is not activatable; review refusal reasons.";
      } else {
        note.textContent = "Preview a pending constraint to enable guarded apply.";
      }
    };
    const invalidatePolicyCandidateActivationPlan = () => {
      currentPolicyCandidateActivationPlan = null;
      currentPolicyCandidateActivationRequest = null;
      const container = document.getElementById("policy-candidate-activation-plan-result");
      if (container.childElementCount) {
        container.replaceChildren(row("Preview required", "Candidate proposal selection changed after the last preview.", "degraded"));
      }
      updatePolicyCandidateActivationApplyButton();
    };
    const renderPolicyCandidateActivationPlan = (plan) => {
      const container = document.getElementById("policy-candidate-activation-plan-result");
      const status = plan.status || "unknown";
      const summaryStatus = status === "review" ? "degraded" : (status === "refused" ? "unavailable" : "available");
      const readSet = (plan.read_set || []).map((item) =>
        compactItem(item.operation || "read", `${item.path || "path not supplied"} / ${item.effect || "effect not supplied"}`)
      );
      const writeSet = (plan.write_set || []).map((item) =>
        compactItem(item.operation || "write", `${item.path || "path not supplied"} / ${item.effect || "effect not supplied"}`)
      );
      const refusals = (plan.refusal_reasons || []).map((item) => compactItem("Refusal", item));
      const warnings = (plan.warnings || []).map((item) => compactItem("Warning", item));
      const nonEffects = (plan.non_effects || []).slice(0, 4).map((item) => compactItem("Non-effect", item));
      const nextActions = (plan.next_actions || []).map((item) => compactItem("Next", item));
      container.replaceChildren(
        row(`Plan ${status}`, `candidate proposal activation / writes performed: ${String(Boolean(plan.writes_performed))}`, summaryStatus),
        compactItem("Target policy", plan.policy_ref || "policy ref not supplied"),
        compactItem("Proposal ref", plan.proposal_ref || "proposal ref not supplied"),
        compactItem("Snapshot", `${plan.proposal_snapshot_status || "unknown"} / ${plan.proposal_sha256 || "sha not supplied"}`),
        compactItem("Manifest status", plan.manifest_status || "manifest status not supplied"),
        ...(readSet.length ? readSet : [compactItem("Read set", "No proposal snapshot read projected.")]),
        ...(writeSet.length ? writeSet : [compactItem("Write set", "No future writes projected.")]),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(nextActions.length ? nextActions : []),
        ...(nonEffects.length ? nonEffects : [])
      );
      updatePolicyCandidateActivationApplyButton();
    };
    const renderPolicyCandidateActivationApplyResult = (result) => {
      const container = document.getElementById("policy-candidate-activation-plan-result");
      const status = result.status || "unknown";
      const summaryStatus = status === "written" ? "available" : "unavailable";
      const writtenPaths = (result.written_paths || []).map((item) => compactItem("Written path", item));
      const createdPaths = (result.created_paths || []).map((item) => compactItem("Created path", item));
      const refusals = (result.refusal_reasons || []).map((item) => compactItem("Refusal", item));
      const warnings = (result.warnings || []).map((item) => compactItem("Warning", item));
      const nextActions = (result.next_actions || []).map((item) => compactItem("Next", item));
      const verification = result.post_write_verification || {};
      container.replaceChildren(
        row(`Apply ${status}`, `candidate proposal activation / write performed: ${String(Boolean(result.write_performed))}`, summaryStatus),
        compactItem("Activated policy", result.policy_ref || "policy ref not supplied"),
        compactItem("Proposal ref", result.proposal_ref || "proposal ref not supplied"),
        compactItem("Decision record", result.decision_record_ref || "decision record not supplied"),
        compactItem("Verification", `active: ${String(Boolean(verification.active_policy_resolvable))} / proposal: ${String(Boolean(verification.proposal_snapshot_existing))}`),
        ...(writtenPaths.length ? writtenPaths : [compactItem("Written paths", "No policy-store writes were reported.")]),
        ...(createdPaths.length ? createdPaths : []),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(nextActions.length ? nextActions : [])
      );
      if (status === "written") {
        currentPolicyCandidateActivationPlan = null;
        currentPolicyCandidateActivationRequest = null;
        updatePolicyCandidateActivationApplyButton();
        fetch("/api/status", {cache: "no-store"}).then((response) => response.json()).then(render);
      }
    };
    const previewPolicyCandidateActivationPlan = () => {
      const button = document.getElementById("policy-candidate-activation-preview-button");
      const container = document.getElementById("policy-candidate-activation-plan-result");
      const requestPayload = policyCandidateActivationRequestFromSelection();
      currentPolicyCandidateActivationPlan = null;
      currentPolicyCandidateActivationRequest = null;
      updatePolicyCandidateActivationApplyButton();
      button.disabled = true;
      button.textContent = "Previewing";
      container.replaceChildren(row("Previewing activation", "Building no-write candidate activation plan.", "degraded"));
      fetch("/api/policy-management/candidate-activation/plan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(requestPayload),
      })
        .then((response) => response.json())
        .then((plan) => {
          currentPolicyCandidateActivationPlan = plan;
          currentPolicyCandidateActivationRequest = requestPayload;
          renderPolicyCandidateActivationPlan(plan);
        })
        .catch((error) => container.replaceChildren(row("Preview failed", error.message, "unavailable")))
        .finally(() => {
          button.disabled = false;
          button.textContent = "Preview activation";
          updatePolicyCandidateActivationApplyButton();
        });
    };
    const applyPolicyCandidateActivationPlan = () => {
      const button = document.getElementById("policy-candidate-activation-apply-button");
      const container = document.getElementById("policy-candidate-activation-plan-result");
      if (!currentPolicyCandidateActivationPlan || !currentPolicyCandidateActivationRequest || !policyCandidateActivationApplyReady(currentPolicyCandidateActivationPlan)) {
        container.replaceChildren(row("Plan required", "Preview and review an activatable policy before applying.", "unavailable"));
        updatePolicyCandidateActivationApplyButton();
        return;
      }
      const writeCount = (currentPolicyCandidateActivationPlan.write_set || []).length;
      const confirmed = window.confirm(
        `Activate this pending policy?\n\nPolicy: ${currentPolicyCandidateActivationPlan.policy_ref || "policy"}\nProposal: ${currentPolicyCandidateActivationPlan.proposal_ref || "proposal"}\nPolicy-store records/files to write: ${writeCount}\n\nThis creates the approved policy file, decision record, and manifest active ref. It does not rewrite the proposal snapshot or execute policy actions.`
      );
      if (!confirmed) {
        return;
      }
      button.disabled = true;
      button.textContent = "Applying";
      fetch("/api/policy-management/candidate-activation/apply", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...currentPolicyCandidateActivationRequest,
          reviewed_proposal_sha256: currentPolicyCandidateActivationPlan.proposal_sha256 || null,
          confirm_apply: true,
          approval_phrase: POLICY_CANDIDATE_ACTIVATION_APPROVAL_PHRASE,
          approval_source: "studio_confirmation_dialog",
        }),
      })
        .then((response) => response.json())
        .then(renderPolicyCandidateActivationApplyResult)
        .catch((error) => container.replaceChildren(row("Apply failed", error.message, "unavailable")))
        .finally(() => {
          button.textContent = "Apply pending policy";
          updatePolicyCandidateActivationApplyButton();
        });
    };
    const policyEvolutionRequest = () => {
      const operation = document.getElementById("policy-evolution-operation").value;
      const policyRef = document.getElementById("policy-evolution-policy").value;
      const feedbackType = document.getElementById("policy-evolution-feedback").value;
      const replacementTitle = document.getElementById("policy-evolution-replacement-title").value.trim();
      const replacementRef = document.getElementById("policy-evolution-replacement-ref").value.trim();
      const triggerMode = document.getElementById("policy-evolution-trigger-mode").value;
      const selectedScopes = selectedOptionValues("policy_evolution_scope");
      const selectedEvents = selectedOptionValues("policy_evolution_lifecycle");
      const currentProfile = selectedPolicyTriggerProfile();
      const currentDeclared = stringValues(currentProfile.declared_trigger_events || (currentProfile.declared_trigger_event ? [currentProfile.declared_trigger_event] : []));
      const replacementScopes = triggerMode === "legacy_event_only" ? [] : selectedScopes;
      const replacementEvents = triggerMode === "scope_first" ? [] : selectedEvents;
      const replacementTrigger = (replacementEvents[0] || selectedEvents[0] || currentDeclared[0] || "task_start").trim();
      const changedPath = document.getElementById("policy-evolution-changed-path").value.trim();
      return {
        policy_ref: policyRef,
        policy_evolution_operation: operation,
        feedback_type: feedbackType || null,
        summary: "Studio active-policy configuration change preview",
        replacement_policy_ref: replacementRef || null,
        replacement_title: replacementTitle || null,
        replacement_trigger_event: replacementTrigger || "task_start",
        replacement_work_profile_policy_scopes: replacementScopes,
        replacement_work_profile_lifecycle_events: replacementEvents,
        replacement_changed_path_pattern: changedPath || null,
      };
    };
    const renderPolicyEvolutionPlan = (plan) => {
      const container = document.getElementById("policy-evolution-plan-result");
      const status = plan.status || "unknown";
      const summaryStatus = status === "review" ? "degraded" : (status === "refused" ? "unavailable" : "available");
      const writeBoundary = plan.future_write_boundary || {};
      const applyReadiness = policyEvolutionApplyReady(plan)
        ? "Studio guarded apply is available after explicit approval."
        : (writeBoundary.writer_implemented
          ? "Core guarded writer exists, but this preview is not ready for apply."
          : "No guarded writer is implemented for this operation yet.");
      const planStatusRows = [
        compactItem("Status reason", plan.status_reason || "No status reason supplied."),
        compactItem("Apply readiness", applyReadiness),
        compactItem("Approval boundary", writeBoundary.requires_guarded_writer ? "guarded approval required before any policy-store write" : "no guarded writer required"),
      ];
      const writeSet = (plan.write_set || []).map((item) =>
        compactItem(item.operation || "write", `${item.path || "path not supplied"} / ${item.effect || "effect not supplied"}`)
      );
      const refusals = (plan.refusal_reasons || []).map((item) =>
        compactItem("Refusal", item)
      );
      const warnings = (plan.warnings || []).map((item) =>
        compactItem("Warning", item)
      );
      const nonEffects = (plan.non_effects || []).slice(0, 4).map((item) =>
        compactItem("Non-effect", item)
      );
      const recommendations = (plan.recommended_changes || []).slice(0, 4).map((item) =>
        compactItem("Next", item)
      );
      const nextActions = (plan.next_actions || []).map((item) =>
        compactItem("Apply next step", item)
      );
      const targetProfile = plan.target_trigger_profile
        ? [compactItem("Current trigger profile", triggerProfileDetailText(plan.target_trigger_profile))]
        : [];
      const proposedProfile = plan.proposed_trigger_profile
        ? [compactItem("Proposed trigger profile", triggerProfileDetailText(plan.proposed_trigger_profile))]
        : [];
      container.replaceChildren(
        row(`Plan ${status}`, `${plan.operation || "operation"} / writes performed: ${String(Boolean(plan.writes_performed))}`, summaryStatus),
        ...planStatusRows,
        compactItem("Target policy", plan.target_policy_ref || "policy ref not supplied"),
        compactItem("Proposal ref", plan.proposal_ref || "proposal ref not supplied"),
        compactItem("Guarded writer", writeBoundary.writer_implemented ? "available in core after approval" : "not available for this operation"),
        ...targetProfile,
        ...proposedProfile,
        ...(writeSet.length ? writeSet : [compactItem("Write set", "No future writes projected.")]),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(recommendations.length ? recommendations : []),
        ...(nextActions.length ? nextActions : []),
        ...(nonEffects.length ? nonEffects : [])
      );
      updatePolicyEvolutionApplyButton();
    };
    const renderPolicyEvolutionApplyResult = (result) => {
      const container = document.getElementById("policy-evolution-plan-result");
      const status = result.status || "unknown";
      const summaryStatus = status === "written" ? "available" : "unavailable";
      const writtenPaths = (result.written_paths || []).map((item) =>
        compactItem("Written path", item)
      );
      const createdPaths = (result.created_paths || []).map((item) =>
        compactItem("Created path", item)
      );
      const refusals = (result.refusal_reasons || []).map((item) =>
        compactItem("Refusal", item)
      );
      const warnings = (result.warnings || []).map((item) =>
        compactItem("Warning", item)
      );
      const nextActions = (result.next_actions || []).map((item) =>
        compactItem("Next", item)
      );
      container.replaceChildren(
        row(`Apply ${status}`, `${result.operation || "operation"} / write performed: ${String(Boolean(result.write_performed))}`, summaryStatus),
        compactItem("Target policy", result.policy_ref || result.target_policy_ref || "policy ref not supplied"),
        compactItem("Proposal ref", result.proposal_ref || "proposal ref not supplied"),
        compactItem("Decision record", result.decision_record_ref || "decision record not supplied"),
        ...(writtenPaths.length ? writtenPaths : [compactItem("Written paths", "No policy-store writes were reported.")]),
        ...(createdPaths.length ? createdPaths : []),
        ...(refusals.length ? refusals : []),
        ...(warnings.length ? warnings : []),
        ...(nextActions.length ? nextActions : [])
      );
      if (status === "written") {
        currentPolicyEvolutionPlan = null;
        currentPolicyEvolutionRequest = null;
        updatePolicyEvolutionApplyButton();
        fetch("/api/status", {cache: "no-store"}).then((response) => response.json()).then(render);
      }
    };
    const previewPolicyEvolutionPlan = () => {
      const button = document.getElementById("policy-evolution-preview-button");
      const container = document.getElementById("policy-evolution-plan-result");
      const requestPayload = policyEvolutionRequest();
      currentPolicyEvolutionPlan = null;
      currentPolicyEvolutionRequest = null;
      updatePolicyEvolutionApplyButton();
      button.disabled = true;
      button.textContent = "Previewing";
      container.replaceChildren(row("Previewing configuration change", "Building no-write active-policy configuration change plan.", "degraded"));
      fetch("/api/policy-management/evolution/plan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(requestPayload),
      })
        .then((response) => response.json())
        .then((plan) => {
          currentPolicyEvolutionPlan = plan;
          currentPolicyEvolutionRequest = requestPayload;
          renderPolicyEvolutionPlan(plan);
        })
        .catch((error) => container.replaceChildren(row("Preview failed", error.message, "unavailable")))
        .finally(() => {
          button.disabled = false;
          button.textContent = "Preview plan";
          updatePolicyEvolutionApplyButton();
        });
    };
    const applyPolicyEvolutionPlan = () => {
      const button = document.getElementById("policy-evolution-apply-button");
      const container = document.getElementById("policy-evolution-plan-result");
      if (!currentPolicyEvolutionPlan || !currentPolicyEvolutionRequest || !policyEvolutionApplyReady(currentPolicyEvolutionPlan)) {
        container.replaceChildren(row("Plan required", "Preview and review a supported active-policy configuration change plan before applying.", "unavailable"));
        updatePolicyEvolutionApplyButton();
        return;
      }
      const writeCount = (currentPolicyEvolutionPlan.write_set || []).length;
      const confirmed = window.confirm(
        `Apply this active-policy configuration change?\n\nTarget: ${currentPolicyEvolutionPlan.target_policy_ref || "policy"}\nOperation: ${currentPolicyEvolutionPlan.operation || "operation"}\nPolicy-store records/files to write: ${writeCount}\n\nThis persists policy-store proposal, decision, manifest, and target/replacement policy records through the guarded writer. It does not execute policy actions.`
          + `${currentPolicyEvolutionPlan.operation === "refine_policy" ? "\\nFor refinement, the target policy trigger profile is updated and reread for verification." : ""}`
      );
      if (!confirmed) {
        return;
      }
      button.disabled = true;
      button.textContent = "Applying";
      fetch("/api/policy-management/evolution/apply", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...currentPolicyEvolutionRequest,
          proposal_ref: currentPolicyEvolutionPlan.proposal_ref || null,
          confirm_apply: true,
          approval_phrase: POLICY_EVOLUTION_APPROVAL_PHRASE,
          approval_source: "studio_confirmation_dialog",
        }),
      })
        .then((response) => response.json())
        .then(renderPolicyEvolutionApplyResult)
        .catch((error) => container.replaceChildren(row("Apply failed", error.message, "unavailable")))
        .finally(() => {
          button.textContent = "Apply guarded change";
          updatePolicyEvolutionApplyButton();
        });
    };
    const renderPolicyManagementFallback = (title, detail, status) => {
      policyManagementReport = null;
      populatePolicyEvolutionTargets({policy_store: {active_policies: []}});
      populatePolicyTemplatePublicationTargets({policy_store: {active_policies: []}});
      populatePolicyTemplateActivationTargets({package_templates: {templates: []}});
      populatePolicyCandidateActivationTargets({policy_store: {activatable_policy_proposals: []}});
      document.getElementById("policy-management-status").className = statusClass(status || "unavailable");
      document.getElementById("policy-management-status").textContent = status || "unavailable";
      document.getElementById("policy-management-metrics").replaceChildren(metric(title, detail));
      ["policy-active-list", "policy-candidate-list", "policy-template-list", "policy-starter-pack-list", "policy-operation-list", "policy-limitation-list", "policy-selected-config", "policy-template-publication-selected-config", "policy-template-selected-config", "policy-candidate-selected-config"].forEach((id) => {
        document.getElementById(id).replaceChildren(compactItem(title, detail));
      });
      document.getElementById("policy-selected-summary").replaceChildren(compactItem(title, detail));
      document.getElementById("policy-selected-trigger-tags").replaceChildren(tag(status || "unavailable", status || "unavailable"));
      document.getElementById("policy-template-publication-selected-summary").replaceChildren(compactItem(title, detail));
      document.getElementById("policy-template-publication-selected-tags").replaceChildren(tag(status || "unavailable", status || "unavailable"));
      document.getElementById("policy-template-selected-summary").replaceChildren(compactItem(title, detail));
      document.getElementById("policy-template-selected-tags").replaceChildren(tag(status || "unavailable", status || "unavailable"));
      document.getElementById("policy-candidate-selected-summary").replaceChildren(compactItem(title, detail));
      document.getElementById("policy-candidate-selected-tags").replaceChildren(tag(status || "unavailable", status || "unavailable"));
    };
    const renderPolicyManagement = (report, studioData) => {
      policyManagementReport = report;
      populatePolicyEvolutionTargets(report);
      populatePolicyTemplatePublicationTargets(report);
      populatePolicyTemplateActivationTargets(report);
      populatePolicyCandidateActivationTargets(report);
      const status = report.status || "unavailable";
      const statusBadge = document.getElementById("policy-management-status");
      statusBadge.className = statusClass(status);
      statusBadge.textContent = status;
      const counts = report.summary_counts || {};
      document.getElementById("policy-management-metrics").replaceChildren(
        metric(counts.active_policy_count || 0, "Active policies"),
        metric(counts.activatable_policy_proposal_count || 0, "Activatable policies")
      );

      const distribution = distributionByPolicyId(report);
      const detailsByPolicy = activePolicyDetailById(report);
      const activePolicies = ((report.policy_store || {}).active_policies || []).map((item) => {
        const dist = distribution[item.policy_id] || {};
        const detail = detailsByPolicy[item.policy_id] || {};
        return policyRecord(
          item.title || item.policy_id,
          `${item.policy_id || "policy id missing"} / ${item.path || "path not supplied"}`,
          item.status || "active",
          [
            policyStatusTag(item.status),
            tag(dist.distribution_state || "distribution unknown", dist.distribution_state === "active_project_policy_only" ? "review" : "available"),
            ...policyProfileTags(detail.trigger_profile || item.applies_to_work_profile),
          ],
          [
            compactItem("Current constraint", triggerProfileDetailText(detail.trigger_profile || item.applies_to_work_profile)),
            compactItem("Required actions", shortRecordList(detail.required_actions, "No required actions declared.")),
            compactItem("Required evidence", shortRecordList(detail.required_evidence, "No required evidence declared.")),
          ]
        );
      });
      const candidateRefs = activatablePolicyProposals(report).map((detail) => {
        const profile = detail.trigger_profile || {};
        return policyRecord(
          detail.title || detail.policy_id || detail.proposal_id || "activatable policy",
          `${detail.policy_id || "policy id missing"} / ${detail.proposal_ref || detail.path || "proposal path not supplied"}`,
          detail.activation_status || "ready_to_activate",
          [
            tag(detail.activation_status || "ready_to_activate", "available"),
            tag(detail.proposal_id || "proposal", "review"),
            tag(detail.manifest_status || "manifest status", "review"),
            ...policyProfileTags(profile),
          ],
          [
            compactItem("Pending constraint", triggerProfileDetailText(profile)),
            compactItem("Required actions if activated", shortRecordList(detail.required_actions, "No required actions declared.")),
            compactItem("Required evidence if activated", shortRecordList(detail.required_evidence, "No required evidence declared.")),
            compactItem("Guarded write", `${detail.write_set_count || 0} policy-store item(s) after approval.`),
          ]
        );
      });
      const templates = ((report.package_templates || {}).templates || []).map((item) =>
        policyRecord(
          item.title || item.template_policy_title || item.template_id,
          `${item.template_policy_id || "policy id missing"} / ${item.template_ref || "template ref not supplied"}`,
          item.portability_status || "template",
          [
            tag(item.namespace || "namespace", "available"),
            tag(`v${item.version || "?"}`, "available"),
            tag(`${item.required_binding_count || 0} bindings`, item.required_binding_count ? "review" : "available"),
            ...templateStarterTags(item.included_in_starter_packs),
          ],
          []
        )
      );
      const starterPacks = ((report.starter_packs || {}).packs || []).map((pack) =>
        policyRecord(
          pack.title || pack.pack_id,
          `${pack.pack_id || "pack id missing"} / ${pack.manifest_ref || "manifest ref not supplied"}`,
          pack.status || "available",
          [
            tag(`${pack.template_count || 0} templates`, "available"),
            tag(pack.status || "available", pack.status || "available"),
          ],
          (pack.policy_templates || []).slice(0, 4).map((item) =>
            compactItem(item.title || item.policy_id || "starter template", item.template_ref || "")
          )
        )
      );
      const reportOperations = (report.available_operations || []).map((item) =>
        policyRecord(
          item.operation || "operation",
          item.surface || "surface not supplied",
          item.write_mode || "no-write",
          [tag(item.write_mode || "no-write", item.write_mode === "guarded-write" ? "guarded" : "available")],
          []
        )
      );
      const studioOperations = ((studioData || {}).available_actions || [])
        .filter((item) => item.domain === "policy_management")
        .map((item) =>
          policyRecord(
            item.title || item.action_id,
            `${item.plan_surface || "plan surface not supplied"}${item.apply_surface ? ` / ${item.apply_surface}` : ""}`,
            item.status || "available",
            [
              tag(item.write_mode || "no-write", item.approval_required ? "guarded" : "available"),
              tag(item.approval_required ? "approval required" : "no approval", item.approval_required ? "guarded" : "available"),
            ],
            []
          )
        );
      const limitations = [
        ...(report.read_model_limitations || []),
        ...(report.non_effects || []),
      ].map((item) => compactItem(item, "Policy management read model boundary"));

      document.getElementById("policy-active-list").replaceChildren(...(activePolicies.length ? activePolicies : [compactItem("No active policies", "Policy store has no active policy refs.")]));
      document.getElementById("policy-candidate-list").replaceChildren(...(candidateRefs.length ? candidateRefs : [compactItem("No activatable policies", "All recorded proposals are already active, already decided, or not ready for guarded activation.")]));
      document.getElementById("policy-template-list").replaceChildren(...(templates.length ? templates : [compactItem("No package templates", "No package policy templates are available.")]));
      document.getElementById("policy-starter-pack-list").replaceChildren(...(starterPacks.length ? starterPacks : [compactItem("No starter packs", "No starter policy-pack manifest is available.")]));
      document.getElementById("policy-operation-list").replaceChildren(...(studioOperations.length ? studioOperations : reportOperations));
      document.getElementById("policy-limitation-list").replaceChildren(...(limitations.length ? limitations : [compactItem("No limitations reported", "Read model reported no limitations.")]));
    };
    const loadPolicyManagement = (studioData) => {
      fetch("/api/policy-management/status", {cache: "no-store"})
        .then((response) => response.json())
        .then((report) => renderPolicyManagement(report, studioData))
        .catch((error) => renderPolicyManagementFallback("Policy management unavailable", error.message, "unavailable"));
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
    const renderSemanticEvidence = (runtime) => {
      const evidence = (runtime || {}).semantic_intent_evidence || {};
      const classification = evidence.classification || {};
      const anchor = evidence.turn_anchor || (runtime || {}).turn_anchor || {};
      const latestRound = evidence.latest_round || {};
      const classificationRound = evidence.classification_round || latestRound;
      const imperfections = evidence.imperfections || [];
      const policyScopes = Array.isArray(classification.policy_scopes)
        ? classification.policy_scopes.join(", ")
        : "";
      const status = document.getElementById("semantic-evidence-status");
      status.className = statusClass(evidence.status || "unavailable");
      status.textContent = evidence.status || "unavailable";
      const list = document.getElementById("semantic-evidence-list");
      list.replaceChildren(
        row(
          "Classified by",
          classification.ai_classified
            ? "Host AI supplied semantic intent to JIKUO for the latest round."
            : `Not proven AI-classified; source=${classification.classification_source || "unknown"}.`,
          classification.ai_classified ? "available" : (evidence.status || "degraded")
        ),
        row(
          "Intent",
          `${classification.intent_class || "unknown"} / scopes: ${policyScopes || "none"} / operation: ${classification.operation_class || "unknown"}`,
          classification.ai_classified ? "available" : (evidence.status || "degraded")
        ),
        row(
          "Latest round",
          `${latestRound.label || latestRound.round_id || "no retained round"} / ${latestRound.lifecycle_event || "event unknown"} / ${latestRound.source_kind || "source unknown"}`,
          latestRound.round_id ? "available" : "unavailable"
        ),
        row(
          "Classification round",
          `${classificationRound.label || classificationRound.round_id || "no retained classification round"} / ${classificationRound.lifecycle_event || "event unknown"} / ${classificationRound.source_kind || "source unknown"}`,
          classification.ai_classified ? "available" : (evidence.status || "degraded")
        ),
        row(
          "Turn anchor",
          anchor.status === "available"
            ? `${anchor.anchor_id || "available"} / session=${anchor.session_id || "unavailable"} / turn=${anchor.turn_id || "unavailable"} / prompt=${anchor.prompt_digest_status || "not_available"} / source=${anchor.evidence_source_kind || anchor.source_kind || "runtime"}`
            : `missing: ${anchor.gap_reason || "turn_anchor_not_supplied_by_host_adapter"}`,
          anchor.status === "available" ? "available" : "degraded"
        ),
        ...(imperfections.length
          ? imperfections.map((item) => row(
              item.title || "Evidence imperfection",
              item.detail || "No detail supplied.",
              item.status || "degraded"
            ))
          : [row("Evidence imperfections", "No additional imperfection is reported for this latest round projection.", "available")])
      );
    };
    const render = (data) => {
      const global = document.getElementById("global-status");
      global.className = statusClass(data.status);
      global.textContent = `${data.status} · no-write`;
      const summaries = data.summaries || {};
      const runtime = summaries.runtime || {};
      const semanticCoverage = runtime.semantic_intent_coverage || {};
      const semanticEvidence = runtime.semantic_intent_evidence || {};
      const policy = summaries.policy_management || {};
      const policyCounts = policy.summary_counts || {};
      const integrations = summaries.integrations || {};
      const mcp = integrations.mcp || {};
      const semanticClassification = semanticEvidence.classification || {};
      const semanticAnchor = semanticEvidence.turn_anchor || runtime.turn_anchor || {};
      const semanticAnchorOverviewValue = semanticAnchor.status === "available"
        ? (semanticAnchor.anchor_id || "available")
        : (semanticAnchor.status || "missing");
      const overview = document.getElementById("overview");
      overview.replaceChildren(
        metric(runtime.status || "unknown", "Runtime"),
        metric(semanticClassification.ai_classified ? "AI" : (semanticClassification.classification_source || semanticEvidence.status || semanticCoverage.coverage_status || "unknown"), "Latest semantic classification"),
        metric(semanticAnchorOverviewValue, "Turn anchor"),
        metric((summaries.document_mounts || {}).checked_document_count || 0, "Completion docs"),
        metric(policyCounts.active_policy_count || 0, "Active policies"),
        metric(policyCounts.package_template_count || 0, "Package templates"),
        metric(mcp.tool_count || 0, "MCP tools"),
        metric((data.pending_user_decisions || []).length, "Pending decisions"),
        metric((data.diagnostics || []).length, "Diagnostics")
      );
      renderSemanticEvidence(runtime);
      renderDocumentMounts(data);
      renderRoundDocumentTrace(data);
      loadPolicyManagement(data);
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
    document.getElementById("policy-evolution-preview-button").addEventListener("click", previewPolicyEvolutionPlan);
    document.getElementById("policy-evolution-apply-button").addEventListener("click", applyPolicyEvolutionPlan);
    ["policy-evolution-operation", "policy-evolution-feedback", "policy-evolution-trigger-mode", "policy-evolution-changed-path", "policy-evolution-replacement-title", "policy-evolution-replacement-ref"].forEach((id) => {
      document.getElementById(id).addEventListener("change", () => {
        if (id === "policy-evolution-trigger-mode") {
          updatePolicyTriggerModeAffordance();
        }
        invalidatePolicyEvolutionPlan();
      });
      document.getElementById(id).addEventListener("input", invalidatePolicyEvolutionPlan);
    });
    ["policy-evolution-scope-options", "policy-evolution-lifecycle-options"].forEach((id) => {
      document.getElementById(id).addEventListener("change", invalidatePolicyEvolutionPlan);
    });
    document.getElementById("policy-evolution-policy").addEventListener("change", () => {
      invalidatePolicyEvolutionPlan();
      renderSelectedPolicyDetail(policyManagementReport || {});
    });
    updatePolicyEvolutionApplyButton();
    document.getElementById("policy-template-activation-preview-button").addEventListener("click", previewPolicyTemplateActivationPlan);
    document.getElementById("policy-template-activation-apply-button").addEventListener("click", applyPolicyTemplateActivationPlan);
    document.getElementById("policy-template-activation-template").addEventListener("change", () => {
      invalidatePolicyTemplateActivationPlan();
      renderSelectedTemplateDetail(policyManagementReport || {});
    });
    document.getElementById("policy-candidate-activation-preview-button").addEventListener("click", previewPolicyCandidateActivationPlan);
    document.getElementById("policy-candidate-activation-apply-button").addEventListener("click", applyPolicyCandidateActivationPlan);
    document.getElementById("policy-candidate-activation-proposal").addEventListener("change", () => {
      invalidatePolicyCandidateActivationPlan();
      renderSelectedCandidateProposalDetail(policyManagementReport || {});
    });
    document.getElementById("policy-template-publication-preview-button").addEventListener("click", previewPolicyTemplatePublicationPlan);
    document.getElementById("policy-template-publication-apply-button").addEventListener("click", applyPolicyTemplatePublicationPlan);
    document.getElementById("policy-template-publication-policy").addEventListener("change", () => {
      invalidatePolicyTemplatePublicationPlan();
      renderSelectedPublicationPolicyDetail(policyManagementReport || {});
    });
    document.getElementById("policy-template-publication-decision").addEventListener("change", invalidatePolicyTemplatePublicationPlan);
    updatePolicyTemplatePublicationApplyButton();
    updatePolicyTemplateActivationApplyButton();
    updatePolicyCandidateActivationApplyButton();
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


def optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def optional_string_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    return string_list(value)


def policy_evolution_args_from_payload(request_payload: dict[str, Any]) -> dict[str, Any]:
    replacement_trigger_event = (
        optional_string(request_payload.get("replacement_trigger_event")) or "task_start"
    )
    return {
        "policy_id": optional_string(request_payload.get("policy_ref")),
        "operation": optional_string(request_payload.get("policy_evolution_operation"))
        or "deprecate_policy",
        "feedback_type": optional_string(request_payload.get("feedback_type")),
        "summary": optional_string(request_payload.get("summary")),
        "source_ref": optional_string(request_payload.get("source_ref"))
        or "studio_policy_evolution_plan_preview",
        "replacement_policy_id": optional_string(
            request_payload.get("replacement_policy_ref")
        ),
        "replacement_title": optional_string(request_payload.get("replacement_title")),
        "replacement_trigger_event": replacement_trigger_event,
        "replacement_work_profile_lifecycle_events": optional_string_list(
            request_payload.get("replacement_work_profile_lifecycle_events")
        ),
        "replacement_work_profile_policy_scopes": optional_string_list(
            request_payload.get("replacement_work_profile_policy_scopes")
        ),
        "replacement_task_type": optional_string(request_payload.get("replacement_task_type")),
        "replacement_jikuo_layer": optional_string(request_payload.get("replacement_jikuo_layer")),
        "replacement_changed_path_pattern": optional_string(
            request_payload.get("replacement_changed_path_pattern")
        ),
        "replacement_added_path_pattern": optional_string(
            request_payload.get("replacement_added_path_pattern")
        ),
        "replacement_action_type": optional_string(
            request_payload.get("replacement_action_type")
        )
        or "render_pre_task_review",
        "replacement_evidence_type": optional_string(
            request_payload.get("replacement_evidence_type")
        )
        or "card_rendered",
    }


def studio_active_policy_path_from_payload(
    request_payload: dict[str, Any],
    *,
    project_root: Path | None = None,
) -> tuple[Path | None, str | None]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    allowed_root = (resolved_root / ".jikuo" / "policies" / "approved").resolve()
    raw_path = optional_string(request_payload.get("source_policy_path")) or optional_string(
        request_payload.get("policy_path")
    )
    raw_ref = optional_string(request_payload.get("policy_ref"))

    if raw_path:
        candidate = Path(raw_path).expanduser()
        if not candidate.is_absolute():
            candidate = resolved_root / candidate
        policy_path = candidate.resolve()
    elif raw_ref:
        if "/" in raw_ref or "\\" in raw_ref:
            return None, f"policy_ref_must_not_include_path_separators:{raw_ref}"
        filename = raw_ref if raw_ref.endswith(".yaml") else f"{raw_ref}.yaml"
        policy_path = (allowed_root / filename).resolve()
    else:
        return None, "policy_ref_or_source_policy_path_required"

    try:
        policy_path.relative_to(allowed_root)
    except ValueError:
        return None, f"source_policy_path_outside_approved_policy_store:{policy_path}"
    if not policy_path.is_file():
        return None, f"source_policy_file_missing:{policy_path}"
    return policy_path, None


def policy_template_publication_args_from_payload(
    request_payload: dict[str, Any],
    *,
    project_root: Path | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    source_policy_path, refusal = studio_active_policy_path_from_payload(
        request_payload,
        project_root=project_root,
    )
    if refusal or source_policy_path is None:
        return None, refusal or "source_policy_required"
    return (
        {
            "source_policy_path": source_policy_path,
            "decision": optional_string(request_payload.get("distribution_decision"))
            or "optional_template",
            "namespace": optional_string(request_payload.get("namespace"))
            or policy_templates.DEFAULT_NAMESPACE,
            "source_project_ref": optional_string(
                request_payload.get("source_project_ref")
            ),
            "starter_pack_id": optional_string(request_payload.get("starter_pack_id"))
            or "engineering_governance",
            "rationale": optional_string(request_payload.get("rationale")),
        },
        None,
    )


def package_policy_templates_root() -> Path:
    return (policy_management_status.package_root() / "policy_templates").resolve()


def studio_policy_template_path_from_payload(
    request_payload: dict[str, Any],
) -> tuple[Path | None, str | None]:
    raw_path = optional_string(request_payload.get("template_path"))
    raw_ref = optional_string(request_payload.get("template_ref")) or optional_string(
        request_payload.get("template")
    )
    if raw_path:
        template_path = Path(raw_path).expanduser().resolve()
    elif raw_ref and raw_ref.startswith("pkg://jikuo/"):
        relative_ref = raw_ref[len("pkg://jikuo/") :]
        template_path = (policy_management_status.package_root() / relative_ref).resolve()
    else:
        return None, "template_ref_or_path_required"

    allowed_root = package_policy_templates_root()
    try:
        template_path.relative_to(allowed_root)
    except ValueError:
        return None, f"template_path_outside_package_policy_templates:{template_path}"
    if not template_path.is_file():
        return None, f"template_file_missing:{template_path}"
    return template_path, None


def template_activation_refusal_payload(
    *,
    request_payload: dict[str, Any],
    refusal_reason: str,
    schema: str,
) -> dict[str, Any]:
    return {
        "schema": schema,
        "schema_version": schema,
        "status": "refused",
        "report_only": schema == policy_templates.POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
        "write_performed": False,
        "writes_performed": False,
        "write_allowed_by_command": False,
        "template_ref": optional_string(request_payload.get("template_ref")),
        "template_path": optional_string(request_payload.get("template_path")),
        "refusal_reasons": [refusal_reason],
        "warnings": [],
        "written_paths": [],
        "created_paths": [],
        "studio_web": {
            "schema": STUDIO_WEB_SCHEMA,
            "route": "policy_template_activation",
            "method": "POST",
            "write_mode": "guarded" if schema == policy_templates.POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA else "no-write-plan",
            "writes_performed": False,
            "write_allowed_by_command": False,
        },
    }


def template_publication_refusal_payload(
    *,
    request_payload: dict[str, Any],
    refusal_reason: str,
    schema: str,
) -> dict[str, Any]:
    return {
        "schema": schema,
        "schema_version": schema,
        "status": "refused",
        "report_only": schema == policy_templates.POLICY_TEMPLATE_PUBLICATION_PLAN_SCHEMA,
        "write_performed": False,
        "writes_performed": False,
        "write_allowed_by_command": False,
        "policy_ref": optional_string(request_payload.get("policy_ref")),
        "source_policy_path": optional_string(request_payload.get("source_policy_path")),
        "distribution_decision": optional_string(
            request_payload.get("distribution_decision")
        ),
        "target_template_path": None,
        "target_template_ref": None,
        "template_ref": None,
        "refusal_reasons": [refusal_reason],
        "warnings": [],
        "written_paths": [],
        "created_paths": [],
        "studio_web": {
            "schema": STUDIO_WEB_SCHEMA,
            "route": "policy_template_publication",
            "method": "POST",
            "write_mode": "guarded"
            if schema == policy_templates.POLICY_TEMPLATE_PUBLICATION_RESULT_SCHEMA
            else "no-write-plan",
            "writes_performed": False,
            "write_allowed_by_command": False,
        },
    }


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


def api_policy_evolution_plan_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy evolution plan requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    plan = policy_store.build_policy_evolution_plan(
        project_root=project_root,
        **policy_evolution_args_from_payload(request_payload),
    )
    plan["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/evolution/plan",
        "method": "POST",
        "write_mode": "no-write-plan",
        "writes_performed": False,
        "write_allowed_by_command": False,
    }
    return HTTPStatus.OK, plan


def api_policy_evolution_apply_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy evolution apply requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    evolution_args = policy_evolution_args_from_payload(request_payload)
    reviewed_proposal_ref = optional_string(request_payload.get("proposal_ref"))
    if reviewed_proposal_ref:
        preview_plan = policy_store.build_policy_evolution_plan(
            project_root=project_root,
            **evolution_args,
        )
        if preview_plan.get("proposal_ref") != reviewed_proposal_ref:
            refusal_reasons = set(preview_plan.get("refusal_reasons") or [])
            refusal_reasons.add("reviewed_proposal_ref_does_not_match_current_request")
            preview_plan["status"] = "refused"
            preview_plan["refusal_reasons"] = sorted(refusal_reasons)
            preview_plan["writes_performed"] = False
            preview_plan["write_allowed_by_command"] = False
            preview_plan["status_reason"] = (
                "policy evolution apply refused because the reviewed proposal ref "
                "does not match the current request payload"
            )
            preview_plan["studio_web"] = {
                "schema": STUDIO_WEB_SCHEMA,
                "route": "/api/policy-management/evolution/apply",
                "method": "POST",
                "write_mode": "guarded",
                "writes_performed": False,
                "write_allowed_by_command": False,
                "reviewed_proposal_ref": reviewed_proposal_ref,
            }
            return HTTPStatus.OK, preview_plan
    result, _exit_code = policy_store.write_policy_evolution_from_plan(
        project_root=project_root,
        **evolution_args,
        confirmed=bool(request_payload.get("confirm_apply")),
        approval_phrase=optional_string(request_payload.get("approval_phrase")),
    )
    result["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/evolution/apply",
        "method": "POST",
        "write_mode": "guarded",
        "writes_performed": bool(result.get("write_performed")),
        "write_allowed_by_command": bool(result.get("write_performed")),
        "approval_source": optional_string(request_payload.get("approval_source")),
        "reviewed_proposal_ref": reviewed_proposal_ref,
    }
    return HTTPStatus.OK, result


def api_policy_template_publication_plan_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy template publication plan requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    publication_args, refusal = policy_template_publication_args_from_payload(
        request_payload,
        project_root=project_root,
    )
    if refusal or publication_args is None:
        payload = template_publication_refusal_payload(
            request_payload=request_payload,
            refusal_reason=refusal or "source_policy_required",
            schema=policy_templates.POLICY_TEMPLATE_PUBLICATION_PLAN_SCHEMA,
        )
        payload["studio_web"]["route"] = "/api/policy-management/template-publication/plan"
        return HTTPStatus.OK, payload
    plan = policy_templates.build_template_publication_plan(**publication_args)
    plan["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/template-publication/plan",
        "method": "POST",
        "write_mode": "no-write-plan",
        "writes_performed": False,
        "write_allowed_by_command": False,
    }
    return HTTPStatus.OK, plan


def api_policy_template_publication_apply_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy template publication apply requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    publication_args, refusal = policy_template_publication_args_from_payload(
        request_payload,
        project_root=project_root,
    )
    if refusal or publication_args is None:
        payload = template_publication_refusal_payload(
            request_payload=request_payload,
            refusal_reason=refusal or "source_policy_required",
            schema=policy_templates.POLICY_TEMPLATE_PUBLICATION_RESULT_SCHEMA,
        )
        payload["studio_web"]["route"] = "/api/policy-management/template-publication/apply"
        return HTTPStatus.OK, payload

    reviewed_source_sha = optional_string(
        request_payload.get("reviewed_source_policy_sha256")
    )
    reviewed_target_path = optional_string(
        request_payload.get("reviewed_target_template_path")
    )
    if reviewed_source_sha or reviewed_target_path:
        preview_plan = policy_templates.build_template_publication_plan(
            **publication_args
        )
        mismatches: list[str] = []
        if reviewed_source_sha and preview_plan.get("source_policy_sha256") != reviewed_source_sha:
            mismatches.append("reviewed_source_policy_sha256_does_not_match_current_source")
        if reviewed_target_path and preview_plan.get("target_template_path") != reviewed_target_path:
            mismatches.append("reviewed_target_template_path_does_not_match_current_request")
        if mismatches:
            payload = template_publication_refusal_payload(
                request_payload=request_payload,
                refusal_reason=";".join(mismatches),
                schema=policy_templates.POLICY_TEMPLATE_PUBLICATION_RESULT_SCHEMA,
            )
            payload["studio_web"]["route"] = "/api/policy-management/template-publication/apply"
            payload["reviewed_source_policy_sha256"] = reviewed_source_sha
            payload["current_source_policy_sha256"] = preview_plan.get(
                "source_policy_sha256"
            )
            payload["reviewed_target_template_path"] = reviewed_target_path
            payload["current_target_template_path"] = preview_plan.get(
                "target_template_path"
            )
            return HTTPStatus.OK, payload

    result, _exit_code = policy_templates.publish_template_from_distribution(
        **publication_args,
        confirmed=bool(request_payload.get("confirm_apply")),
        approval_phrase=optional_string(request_payload.get("approval_phrase")),
    )
    result["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/template-publication/apply",
        "method": "POST",
        "write_mode": "guarded",
        "writes_performed": bool(result.get("write_performed")),
        "write_allowed_by_command": bool(result.get("write_performed")),
        "approval_source": optional_string(request_payload.get("approval_source")),
        "reviewed_source_policy_sha256": reviewed_source_sha,
        "reviewed_target_template_path": reviewed_target_path,
    }
    return HTTPStatus.OK, result


def api_policy_template_activation_plan_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy template activation plan requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    template_path, refusal = studio_policy_template_path_from_payload(request_payload)
    if refusal or template_path is None:
        payload = template_activation_refusal_payload(
            request_payload=request_payload,
            refusal_reason=refusal or "template_ref_or_path_required",
            schema=policy_templates.POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
        )
        payload["studio_web"]["route"] = "/api/policy-management/template-activation/plan"
        return HTTPStatus.OK, payload
    plan = policy_templates.build_import_plan(
        template_path=template_path,
        project_root=project_root,
    )
    plan["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/template-activation/plan",
        "method": "POST",
        "write_mode": "no-write-plan",
        "writes_performed": False,
        "write_allowed_by_command": False,
    }
    return HTTPStatus.OK, plan


def api_policy_template_activation_apply_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy template activation apply requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    template_path, refusal = studio_policy_template_path_from_payload(request_payload)
    if refusal or template_path is None:
        payload = template_activation_refusal_payload(
            request_payload=request_payload,
            refusal_reason=refusal or "template_ref_or_path_required",
            schema=policy_templates.POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
        )
        payload["studio_web"]["route"] = "/api/policy-management/template-activation/apply"
        return HTTPStatus.OK, payload

    reviewed_plan_id = optional_string(request_payload.get("plan_id"))
    if reviewed_plan_id:
        preview_plan = policy_templates.build_import_plan(
            template_path=template_path,
            project_root=project_root,
        )
        if preview_plan.get("plan_id") != reviewed_plan_id:
            payload = template_activation_refusal_payload(
                request_payload=request_payload,
                refusal_reason="reviewed_plan_id_does_not_match_current_request",
                schema=policy_templates.POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
            )
            payload["studio_web"]["route"] = "/api/policy-management/template-activation/apply"
            payload["reviewed_plan_id"] = reviewed_plan_id
            payload["current_plan_id"] = preview_plan.get("plan_id")
            return HTTPStatus.OK, payload

    result, _exit_code = policy_templates.activate_template_from_plan(
        template_path=template_path,
        project_root=project_root,
        confirmed=bool(request_payload.get("confirm_apply")),
        approval_phrase=optional_string(request_payload.get("approval_phrase")),
    )
    result["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/template-activation/apply",
        "method": "POST",
        "write_mode": "guarded",
        "writes_performed": bool(result.get("write_performed")),
        "write_allowed_by_command": bool(result.get("write_performed")),
        "approval_source": optional_string(request_payload.get("approval_source")),
        "reviewed_plan_id": reviewed_plan_id,
    }
    return HTTPStatus.OK, result


def api_policy_candidate_activation_plan_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy candidate activation plan requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    plan = policy_store.build_policy_proposal_activation_plan(
        project_root=project_root,
        proposal_ref=optional_string(request_payload.get("proposal_ref")),
        proposal_id=optional_string(request_payload.get("proposal_id")),
    )
    plan["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/candidate-activation/plan",
        "method": "POST",
        "write_mode": "no-write-plan",
        "writes_performed": False,
        "write_allowed_by_command": False,
    }
    return HTTPStatus.OK, plan


def api_policy_candidate_activation_apply_payload(
    request_payload: Any,
    *,
    project_root: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(request_payload, dict):
        return HTTPStatus.BAD_REQUEST, {
            "schema": STUDIO_WEB_SCHEMA,
            "status": "invalid_request",
            "message": "policy candidate activation apply requests must be JSON objects",
            "writes_performed": False,
            "write_allowed_by_command": False,
        }
    result, _exit_code = policy_store.activate_policy_proposal_from_snapshot(
        project_root=project_root,
        proposal_ref=optional_string(request_payload.get("proposal_ref")),
        proposal_id=optional_string(request_payload.get("proposal_id")),
        reviewed_proposal_sha256=optional_string(
            request_payload.get("reviewed_proposal_sha256")
        ),
        confirmed=bool(request_payload.get("confirm_apply")),
        approval_phrase=optional_string(request_payload.get("approval_phrase")),
    )
    result["studio_web"] = {
        "schema": STUDIO_WEB_SCHEMA,
        "route": "/api/policy-management/candidate-activation/apply",
        "method": "POST",
        "write_mode": "guarded",
        "writes_performed": bool(result.get("write_performed")),
        "write_allowed_by_command": bool(result.get("write_performed")),
        "approval_source": optional_string(request_payload.get("approval_source")),
        "reviewed_proposal_sha256": optional_string(
            request_payload.get("reviewed_proposal_sha256")
        ),
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
    if route == "/api/policy-management/status":
        return HTTPStatus.OK, policy_management_status.build_policy_management_status(
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
            if route not in {
                "/api/document-rules/plan",
                "/api/document-rules/apply",
                "/api/policy-management/evolution/plan",
                "/api/policy-management/evolution/apply",
                "/api/policy-management/template-publication/plan",
                "/api/policy-management/template-publication/apply",
                "/api/policy-management/template-activation/plan",
                "/api/policy-management/template-activation/apply",
                "/api/policy-management/candidate-activation/plan",
                "/api/policy-management/candidate-activation/apply",
            }:
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
            elif route == "/api/document-rules/apply":
                status, payload = api_document_rules_apply_payload(
                    request_payload,
                    project_root=project_root,
                )
            elif route == "/api/policy-management/evolution/plan":
                status, payload = api_policy_evolution_plan_payload(
                    request_payload,
                    project_root=project_root,
                )
            elif route == "/api/policy-management/evolution/apply":
                status, payload = api_policy_evolution_apply_payload(
                    request_payload,
                    project_root=project_root,
                )
            elif route == "/api/policy-management/template-publication/plan":
                status, payload = api_policy_template_publication_plan_payload(
                    request_payload,
                    project_root=project_root,
                )
            elif route == "/api/policy-management/template-publication/apply":
                status, payload = api_policy_template_publication_apply_payload(
                    request_payload,
                    project_root=project_root,
                )
            elif route == "/api/policy-management/template-activation/plan":
                status, payload = api_policy_template_activation_plan_payload(
                    request_payload,
                    project_root=project_root,
                )
            elif route == "/api/policy-management/template-activation/apply":
                status, payload = api_policy_template_activation_apply_payload(
                    request_payload,
                    project_root=project_root,
                )
            elif route == "/api/policy-management/candidate-activation/plan":
                status, payload = api_policy_candidate_activation_plan_payload(
                    request_payload,
                    project_root=project_root,
                )
            else:
                status, payload = api_policy_candidate_activation_apply_payload(
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
