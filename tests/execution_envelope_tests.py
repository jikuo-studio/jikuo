import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jikuo import execution_envelope, private_turn_input_index, turn_anchor


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "agent_flow.py"
READY_PROJECT = ROOT / "src" / "jikuo" / "fixtures" / "task_session_ready_project"


class ExecutionEnvelopeTests(unittest.TestCase):
    def test_execution_envelope_wraps_turn_anchor_without_raw_prompt(self):
        raw_prompt = "SECRET_EXECUTION_ENVELOPE_PROMPT: implement the CLI wrapper"
        anchor = turn_anchor.build_turn_anchor(
            client_id="codex",
            client_event="UserPromptSubmit",
            session_id="session-envelope",
            turn_id="turn-envelope",
            received_at_utc="2026-06-05T00:00:00Z",
            raw_prompt=raw_prompt,
        )
        semantic = {
            "schema": "jikuo.host_semantic_intent.v0",
            "status": "provided",
            "provider": "host_ai",
            "confidence": "high",
            "policy_scopes": ["editing", "progress_summary"],
            "policy_contract": {
                "requested_outcome": "implement CLI enhanced envelope",
                "execution_boundary": "project-local code and tests",
                "response_contract": ["summarize verification"],
            },
            "turn_anchor": anchor,
        }

        envelope = execution_envelope.build_execution_envelope(
            project_root=ROOT,
            turn_anchor=anchor,
            host_semantic_intent=semantic,
            lifecycle_event="task_start",
        )
        serialized = json.dumps(envelope, ensure_ascii=False)

        self.assertEqual(envelope["schema"], "jikuo.execution_envelope.v0")
        self.assertEqual(envelope["lifecycle"]["state"], "task_started")
        self.assertEqual(envelope["turn_anchor"]["anchor_id"], anchor["anchor_id"])
        self.assertEqual(envelope["host_semantic_intent"]["provider"], "host_ai")
        self.assertEqual(envelope["privacy"]["raw_prompt_storage"], "none")
        self.assertFalse(envelope["privacy"]["raw_prompt_exposed_in_audit"])
        self.assertNotIn(raw_prompt, serialized)

    def test_execution_envelope_sanitizes_private_input_ref(self):
        raw_prompt = "SECRET_PRIVATE_REF_PROMPT: search this later"
        anchor = turn_anchor.build_turn_anchor(
            session_id="session-private-ref",
            turn_id="turn-private-ref",
            raw_prompt=raw_prompt,
        )
        private_ref = private_turn_input_index.build_index_ref(
            project_root=ROOT,
            turn_anchor=anchor,
            raw_input_present=True,
            record_id="input_test",
            write_performed=True,
        )
        private_ref["raw_user_input"] = raw_prompt

        envelope = execution_envelope.build_execution_envelope(
            project_root=ROOT,
            turn_anchor=anchor,
            lifecycle_event="completion_review",
            private_turn_input_ref=private_ref,
        )
        serialized = json.dumps(envelope, ensure_ascii=False)

        self.assertEqual(envelope["lifecycle"]["state"], "completion_reviewed")
        self.assertEqual(envelope["privacy"]["raw_prompt_storage"], "private_index")
        self.assertEqual(
            envelope["links"]["private_turn_input_ref"]["record_id"],
            "input_test",
        )
        self.assertNotIn(raw_prompt, serialized)

    def test_agent_flow_projects_private_input_ref_into_runtime_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)
            raw_prompt = "SECRET_AGENT_FLOW_PRIVATE_REF_PROMPT"
            anchor = turn_anchor.build_turn_anchor(
                session_id="session-agent-flow-private",
                turn_id="turn-agent-flow-private",
                raw_prompt=raw_prompt,
            )
            private_ref = private_turn_input_index.build_index_ref(
                project_root=project_root,
                turn_anchor=anchor,
                raw_input_present=True,
                record_id="input_agent_flow_private_ref",
                write_performed=False,
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Execution Envelope Private Ref Probe",
                    "--project-root",
                    str(project_root),
                    "--turn-anchor-json",
                    json.dumps(anchor, separators=(",", ":")),
                    "--private-turn-input-ref-json",
                    json.dumps(private_ref, separators=(",", ":")),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            proposal = json.loads(completed.stdout)
            envelope = proposal["execution_envelope"]
            self.assertEqual(envelope["lifecycle"]["state"], "task_started")
            self.assertEqual(
                envelope["links"]["private_turn_input_ref"]["record_id"],
                "input_agent_flow_private_ref",
            )
            self.assertEqual(
                envelope["links"]["runtime_refs"]["history_ref"],
                proposal["runtime_visibility"]["history_ref"],
            )
            self.assertNotIn(raw_prompt, json.dumps(proposal, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
