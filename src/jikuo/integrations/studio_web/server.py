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
    from ...studio import global_status
else:  # pragma: no cover - direct module execution fallback
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from jikuo.studio import global_status


STUDIO_WEB_SCHEMA = "jikuo.studio.web_console.v0"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


INDEX_HTML = """<!doctype html>
<html lang="en" data-jikuo-studio="read-only">
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
    @media (max-width: 700px) {
      header { align-items: flex-start; flex-direction: column; }
      main { padding: 18px 16px 32px; }
      .row { grid-template-columns: 1fr; }
      .split { grid-template-columns: 1fr; }
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
          <p class="subhead" id="rule-sources-label">Rule sources and edit status</p>
          <div class="list" id="document-mounts-authority"></div>
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
      document.getElementById("rule-sources-label").textContent = `${termLabel(terms, "rule_sources", "Current rule sources")} and ${termLabel(terms, "edit_status", "how changes are applied").toLowerCase()}`;
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
      const authority = document.getElementById("document-mounts-authority");
      const authorityRows = (mounts.active_mount_authority || []).map((item) =>
        row(item, termDescription(terms, "rule_sources", "Where JIKUO currently reads the document rules for this project."), "available")
      );
      const missing = mounts.missing_required_roles || [];
      authority.replaceChildren(
        ...authorityRows,
        row(termLabel(terms, "edit_status", "How changes are applied"), planAction.disabled_reason || "available", planAction.status || "available"),
        ...(missing.length ? missing.slice(0, 4).map((item) =>
          row(item.role || "missing role", item.path || "unbound", "warning")
        ) : [emptyRow("No required document roles are missing.")])
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
  </script>
</body>
</html>
"""


def json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


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
    print(f"JIKUO Studio read-only console: http://{actual_host}:{actual_port}/")
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
