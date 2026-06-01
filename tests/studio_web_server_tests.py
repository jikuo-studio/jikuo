import json
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.integrations.studio_web import server  # noqa: E402


class StudioWebServerTests(unittest.TestCase):
    def test_api_payloads_are_read_only_status_views(self):
        status_code, status = server.api_payload_for_path("/api/status", project_root=ROOT)
        panels_code, panels = server.api_payload_for_path("/api/panels", project_root=ROOT)
        actions_code, actions = server.api_payload_for_path("/api/actions", project_root=ROOT)
        health_code, health = server.api_payload_for_path("/api/health", project_root=ROOT)

        self.assertEqual(status_code, 200)
        self.assertEqual(panels_code, 200)
        self.assertEqual(actions_code, 200)
        self.assertEqual(health_code, 200)
        self.assertEqual(status["schema"], "jikuo.studio.global_status.v0")
        self.assertEqual(panels["schema"], "jikuo.studio.panel_registry.v0")
        self.assertEqual(actions["schema"], "jikuo.studio.action_registry.v0")
        self.assertEqual(health["schema"], server.STUDIO_WEB_SCHEMA)
        self.assertFalse(status["writes_performed"])
        self.assertFalse(panels["writes_performed"])
        self.assertFalse(actions["writes_performed"])
        self.assertFalse(health["writes_performed"])

    def test_index_html_is_static_read_only_shell(self):
        html = server.render_index_html()

        self.assertIn("data-jikuo-studio=\"read-only\"", html)
        self.assertIn("JIKUO Studio", html)
        self.assertIn("/api/status", html)
        self.assertIn("Document Rules", html)
        self.assertIn("document-mounts-completion", html)
        self.assertIn("Available Actions", html)
        self.assertNotIn("Mount authority and pending write boundary", html)
        self.assertNotIn("approval-phrase", html)

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

            self.assertIn("JIKUO Studio", html)
            self.assertIn("Document Rules", html)
            self.assertEqual(status["schema"], "jikuo.studio.global_status.v0")
            self.assertIn("document_mounts", status["summaries"])
            terms = {
                item["term_id"]: item
                for item in status["summaries"]["document_mounts"]["configuration_terms"]
            }
            self.assertIn("rule_sources", terms)
            self.assertEqual(panels["schema"], "jikuo.studio.panel_registry.v0")
            self.assertEqual(actions["schema"], "jikuo.studio.action_registry.v0")
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

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
