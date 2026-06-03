import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.integrations.studio_web import server  # noqa: E402


def write_project_context(root: Path) -> None:
    jikuo = root / ".jikuo"
    jikuo.mkdir(parents=True, exist_ok=True)
    (jikuo / "project_context.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.project_context.v0"',
                "document_roles:",
                "  project_context:",
                '    path: ".jikuo/project_context.yaml"',
                "    required: true",
                '    note: "Project context."',
                "main_document_mounts:",
                '  canonical_path_root: "."',
                '  path_policy: "standalone_repo_paths_only"',
                "  active_mount_authority:",
                '    - ".jikuo/project_context.yaml"',
                "  checked_before_slice_completion:",
                '    - path: ".jikuo/project_context.yaml"',
                '      update_required_when: "document rules change"',
                "  unchanged_report_required: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def touch(root: Path, rel: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {path.name}\n", encoding="utf-8")


class StudioWebServerTests(unittest.TestCase):
    def test_api_payloads_are_read_only_status_views(self):
        status_code, status = server.api_payload_for_path("/api/status", project_root=ROOT)
        panels_code, panels = server.api_payload_for_path("/api/panels", project_root=ROOT)
        actions_code, actions = server.api_payload_for_path("/api/actions", project_root=ROOT)
        files_code, files = server.api_payload_for_path("/api/project-files", project_root=ROOT)
        health_code, health = server.api_payload_for_path("/api/health", project_root=ROOT)

        self.assertEqual(status_code, 200)
        self.assertEqual(panels_code, 200)
        self.assertEqual(actions_code, 200)
        self.assertEqual(files_code, 200)
        self.assertEqual(health_code, 200)
        self.assertEqual(status["schema"], "jikuo.studio.global_status.v0")
        self.assertIn("artifact_assurance", status["summaries"])
        self.assertIn("artifact_assurance", status["summaries"]["runtime"])
        self.assertEqual(panels["schema"], "jikuo.studio.panel_registry.v0")
        self.assertEqual(actions["schema"], "jikuo.studio.action_registry.v0")
        self.assertEqual(files["schema"], "jikuo.studio.project_file_inventory.v0")
        self.assertEqual(health["schema"], server.STUDIO_WEB_SCHEMA)
        self.assertFalse(status["writes_performed"])
        self.assertFalse(panels["writes_performed"])
        self.assertFalse(actions["writes_performed"])
        self.assertFalse(files["writes_performed"])
        self.assertFalse(health["writes_performed"])

    def test_document_rules_plan_api_returns_no_write_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/customer-guide.md")

            status_code, plan = server.api_document_rules_plan_payload(
                {
                    "add_context_docs": ["docs/customer-guide.md"],
                    "add_completion_checks": ["docs/customer-guide.md"],
                    "add_governance_references": ["docs/customer-guide.md"],
                    "completion_update_rule": "customer guide changes",
                    "selection_records": [
                        {
                            "path": "docs/customer-guide.md",
                            "selected_at_utc": "2026-06-02T00:00:00Z",
                        }
                    ],
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["schema"], "jikuo.studio.document_rules_update_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertEqual(plan["change_count"], 3)
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(plan["studio_web"]["route"], "/api/document-rules/plan")
            self.assertEqual(
                plan["studio_web"]["selection_records"][0]["selected_at_utc"],
                "2026-06-02T00:00:00Z",
            )

    def test_document_rules_plan_api_surfaces_refused_validation_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)

            status_code, plan = server.api_document_rules_plan_payload(
                {"add_context_docs": ["../outside.md"]},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["status"], "refused")
            self.assertFalse(plan["writes_performed"])
            self.assertIn(
                "path_outside_project_root",
                {item["code"] for item in plan["validation"]["errors"]},
            )

    def test_index_html_is_no_write_control_shell_with_document_rules_preview(self):
        html = server.render_index_html()

        self.assertIn("data-jikuo-studio=\"guarded-control-shell\"", html)
        self.assertIn("JIKUO Studio", html)
        self.assertIn("/api/status", html)
        self.assertIn("/api/project-files", html)
        self.assertIn("/api/document-rules/plan", html)
        self.assertIn("/api/document-rules/apply", html)
        self.assertIn("Document Rules", html)
        self.assertIn("Round Document Trace", html)
        self.assertIn("Select a runtime round to inspect expected documents", html)
        self.assertIn("round-trace-rounds", html)
        self.assertIn("No document changes", html)
        self.assertIn("Document changes", html)
        self.assertIn("Expected", html)
        self.assertIn("Observed", html)
        self.assertIn("Gaps", html)
        self.assertIn("Action chain", html)
        self.assertIn("round-trace-summary", html)
        self.assertIn("round-trace-expected", html)
        self.assertIn("round-trace-observed", html)
        self.assertIn("round-trace-gaps", html)
        self.assertIn("round-trace-timeline", html)
        self.assertIn("No comparable trace was captured", html)
        self.assertIn("const selectedCounts = (selectedRound || {}).counts || {}", html)
        self.assertIn("const active = latestAvailable ? activeTrace : {}", html)
        self.assertIn("const artifactCount = (items, ...counts)", html)
        self.assertIn("Detailed item paths are not available in this history card", html)
        self.assertIn("Detailed gap categories are not available in this history card", html)
        self.assertNotIn("artifact-assurance-metrics", html)
        self.assertIn("Current Document Rules", html)
        self.assertIn("Each column is one Document Rules purpose", html)
        self.assertIn("Context documents", html)
        self.assertIn("Source: document roles", html)
        self.assertIn("Completion checks", html)
        self.assertIn("Source: completion-check rules", html)
        self.assertIn("Governance references", html)
        self.assertIn("Source: rule-source references", html)
        self.assertIn("Add files to Document Rules", html)
        self.assertIn("Candidate local files", html)
        self.assertIn("In Document Rules", html)
        self.assertIn("Not in Document Rules", html)
        self.assertIn("Context document", html)
        self.assertIn("Completion check", html)
        self.assertIn("Governance reference", html)
        self.assertNotIn("document-mounts-completion", html)
        self.assertNotIn("document-mounts-editable-sources", html)
        self.assertNotIn("document-mounts-guidance-sources", html)
        self.assertIn("document-rules-form", html)
        self.assertIn("document-rules-file-list", html)
        self.assertIn("document-rules-selected-files", html)
        self.assertIn("document-rules-clear-selection", html)
        self.assertIn("Preview plan", html)
        self.assertIn("document-rules-apply-note", html)
        self.assertIn("Approve and apply", html)
        self.assertIn("window.confirm", html)
        self.assertIn("Approve Document Rules update", html)
        self.assertIn("studio_confirmation_dialog", html)
        self.assertNotIn("document-rules-approval-phrase", html)
        self.assertNotIn('name="approval_phrase"', html)
        self.assertIn("Available Actions", html)
        self.assertNotIn("Mount authority and pending write boundary", html)
        self.assertNotIn("Current rule sources", html)

    def test_http_server_serves_index_and_json_endpoints(self):
        httpd = server.create_server(host="127.0.0.1", port=0, project_root=ROOT)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = httpd.server_address
            base_url = f"http://{host}:{port}"

            with urlopen(f"{base_url}/", timeout=10) as response:
                html = response.read().decode("utf-8")
            with urlopen(f"{base_url}/api/status", timeout=10) as response:
                status = json.loads(response.read().decode("utf-8"))
            with urlopen(f"{base_url}/api/panels", timeout=10) as response:
                panels = json.loads(response.read().decode("utf-8"))
            with urlopen(f"{base_url}/api/actions", timeout=10) as response:
                actions = json.loads(response.read().decode("utf-8"))
            with urlopen(f"{base_url}/api/project-files", timeout=10) as response:
                files = json.loads(response.read().decode("utf-8"))

            self.assertIn("JIKUO Studio", html)
            self.assertIn("Document Rules", html)
            self.assertEqual(status["schema"], "jikuo.studio.global_status.v0")
            self.assertIn("document_mounts", status["summaries"])
            self.assertIn("artifact_assurance", status["summaries"])
            self.assertIn("artifact_assurance", status["summaries"]["runtime"])
            terms = {
                item["term_id"]: item
                for item in status["summaries"]["document_mounts"]["configuration_terms"]
            }
            self.assertIn("rule_sources", terms)
            self.assertIn("editable_configuration", terms)
            self.assertIn("governance_guidance", terms)
            self.assertTrue(
                status["summaries"]["document_mounts"]["editable_configuration_sources"]
            )
            self.assertTrue(
                status["summaries"]["document_mounts"]["governance_guidance_sources"]
            )
            self.assertEqual(panels["schema"], "jikuo.studio.panel_registry.v0")
            self.assertEqual(actions["schema"], "jikuo.studio.action_registry.v0")
            self.assertEqual(files["schema"], "jikuo.studio.project_file_inventory.v0")
            self.assertFalse(files["writes_performed"])
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

    def test_http_server_accepts_document_rules_plan_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/customer-guide.md")
            httpd = server.create_server(host="127.0.0.1", port=0, project_root=project_root)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = httpd.server_address
                payload = json.dumps(
                    {"add_context_docs": ["docs/customer-guide.md"]}
                ).encode("utf-8")
                request = Request(
                    f"http://{host}:{port}/api/document-rules/plan",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=10) as response:
                    plan = json.loads(response.read().decode("utf-8"))

                self.assertEqual(plan["schema"], "jikuo.studio.document_rules_update_plan.v0")
                self.assertEqual(plan["status"], "review")
                self.assertFalse(plan["writes_performed"])
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=10)

    def test_document_rules_apply_api_refuses_then_applies_reviewed_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/customer-guide.md")
            status_code, plan = server.api_document_rules_plan_payload(
                {"add_context_docs": ["customer_guide=docs/customer-guide.md"]},
                project_root=project_root,
            )

            refused_code, refused = server.api_document_rules_apply_payload(
                {"plan": plan, "confirm_apply": False},
                project_root=project_root,
            )
            applied_code, applied = server.api_document_rules_apply_payload(
                {
                    "plan": plan,
                    "confirm_apply": True,
                    "approval_phrase": "Approve Document Rules update",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(refused_code, 200)
            self.assertEqual(refused["status"], "refused")
            self.assertFalse(refused["write_performed"])
            self.assertEqual(applied_code, 200)
            self.assertEqual(applied["status"], "applied")
            self.assertTrue(applied["write_performed"])
            self.assertEqual(applied["studio_web"]["route"], "/api/document-rules/apply")
            context, errors = server.document_rules.load_project_context(project_root)
            self.assertEqual(errors, [])
            self.assertEqual(
                context["document_roles"]["customer_guide"]["path"],
                "docs/customer-guide.md",
            )

    def test_http_server_returns_structured_not_found(self):
        httpd = server.create_server(host="127.0.0.1", port=0, project_root=ROOT)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = httpd.server_address
            with self.assertRaises(HTTPError) as caught:
                urlopen(f"http://{host}:{port}/missing", timeout=10)
            self.assertEqual(caught.exception.code, 404)
            try:
                payload = json.loads(caught.exception.read().decode("utf-8"))
            finally:
                caught.exception.close()
            self.assertEqual(payload["status"], "not_found")
            self.assertFalse(payload["writes_performed"])
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

    def test_root_cli_exposes_studio_serve_help_without_starting_server(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "jikuo",
                "studio",
                "--help",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("serve", completed.stdout)
        self.assertIn("--host", completed.stdout)
        self.assertIn("--port", completed.stdout)


if __name__ == "__main__":
    unittest.main()
