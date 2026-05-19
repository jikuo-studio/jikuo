import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK_SCRIPT = ROOT / ".codex" / "hooks" / "jikuo_user_prompt_submit.py"


def load_hook_module():
    spec = importlib.util.spec_from_file_location("jikuo_user_prompt_submit", HOOK_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CodexHookProofTests(unittest.TestCase):
    def test_extract_hook_input_accepts_codex_user_prompt_submit_payload(self):
        hook = load_hook_module()
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Please update the hook docs.",
            "cwd": str(ROOT / "docs"),
            "session_id": "session-1",
            "turn_id": "turn-1",
            "permission_mode": "default",
            "model": "gpt-test",
        }

        hook_input = hook.extract_hook_input(payload, {})

        self.assertEqual(hook_input.hook_event_name, "UserPromptSubmit")
        self.assertEqual(hook_input.prompt, "Please update the hook docs.")
        self.assertEqual(hook_input.cwd, ROOT / "docs")
        self.assertEqual(hook_input.session_id, "session-1")
        self.assertEqual(hook_input.turn_id, "turn-1")
        self.assertEqual(hook_input.permission_mode, "default")
        self.assertEqual(hook_input.model, "gpt-test")

    def test_render_additional_context_omits_raw_prompt(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: please edit files"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-2",
            turn_id="turn-2",
            permission_mode="default",
            model=None,
        )
        proposal = {
            "runtime_visibility": {
                "last_card_ref": ".jikuo/runtime/last_card.md",
                "history_ref": ".jikuo/runtime/history/proposal.md",
            },
            "client_display_links": {
                "links": {
                    "last_card": {"markdown": "[last_card.md](D:/x/.jikuo/runtime/last_card.md)"},
                    "history_card": {"markdown": "[proposal.md](D:/x/.jikuo/runtime/history/proposal.md)"},
                }
            },
            "work_profile": {
                "lifecycle_event": "conversation_turn",
                "policy_scopes": ["editing"],
            },
            "triggered_policies": [{"policy_ref": "POLICY-test"}],
            "missing_evidence_reports": [{"report_id": "missing-1"}],
            "conversation_router": {
                "required_followup_tools": ["jikuo.propose_task_start"],
            },
        }

        context = hook.render_additional_context(
            proposal,
            hook_input,
            ROOT,
            "mounted",
            semantic_intent_status="unavailable",
        )

        self.assertNotIn(raw_prompt, context)
        self.assertIn("JIKUO mounted pre-turn ran", context)
        self.assertIn("Semantic intent status: unavailable.", context)
        self.assertIn("Triggered policy count: 1.", context)
        self.assertIn("Missing evidence report count: 1.", context)
        self.assertIn("jikuo.propose_task_start", context)
        self.assertIn("Durable writes remain guarded", context)

    def test_build_agent_flow_command_uses_stdin_flag_without_raw_prompt(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: implement proof"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-command",
            turn_id="turn-command",
            permission_mode="default",
            model=None,
        )

        command = hook.build_agent_flow_command(
            hook_input,
            ROOT,
            "mounted",
            env={"JIKUO_HOOK_PYTHON": "python"},
        )

        self.assertIn("--user-phrase-stdin", command)
        self.assertNotIn("--user-phrase", command)
        self.assertNotIn(raw_prompt, command)

    def test_main_emits_codex_additional_context_with_fake_runner(self):
        hook = load_hook_module()
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "SECRET_PROMPT_VALUE: implement proof",
            "cwd": str(ROOT),
            "session_id": "session-3",
            "turn_id": "turn-3",
            "permission_mode": "default",
        }

        def fake_runner(hook_input, project_root, trigger_mode):
            self.assertEqual(hook_input.turn_id, "turn-3")
            self.assertEqual(project_root, ROOT)
            self.assertEqual(trigger_mode, "mounted")
            return {
                "runtime_visibility": {
                    "last_card_ref": ".jikuo/runtime/last_card.md",
                    "history_ref": ".jikuo/runtime/history/proposal.md",
                },
                "work_profile": {
                    "lifecycle_event": "conversation_turn",
                    "policy_scopes": ["editing"],
                },
                "triggered_policies": [],
                "missing_evidence_reports": [],
            }

        stdout = io.StringIO()
        exit_code = hook.main(
            stdin=io.StringIO(json.dumps(payload)),
            stdout=stdout,
            runner=fake_runner,
            env={"JIKUO_HOOK_TRIGGER_MODE": "mounted"},
        )

        self.assertEqual(exit_code, 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"],
            "UserPromptSubmit",
        )
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("JIKUO mounted pre-turn ran", additional_context)
        self.assertIn("Latest card: .jikuo/runtime/last_card.md", additional_context)
        self.assertNotIn(payload["prompt"], additional_context)

    def test_main_reports_visible_degradation_on_runner_failure(self):
        hook = load_hook_module()
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "SECRET_PROMPT_VALUE: implement proof",
            "cwd": str(ROOT),
            "session_id": "session-4",
            "turn_id": "turn-4",
            "permission_mode": "default",
        }

        def failing_runner(hook_input, project_root, trigger_mode):
            raise hook.HookExecutionError("simulated failure")

        stdout = io.StringIO()
        exit_code = hook.main(
            stdin=io.StringIO(json.dumps(payload)),
            stdout=stdout,
            runner=failing_runner,
            env={},
        )

        self.assertEqual(exit_code, 0)
        output = json.loads(stdout.getvalue())
        self.assertIn("systemMessage", output)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("JIKUO mounted pre-turn failed", additional_context)
        self.assertIn("simulated failure", additional_context)
        self.assertNotIn(payload["prompt"], additional_context)


if __name__ == "__main__":
    unittest.main()
