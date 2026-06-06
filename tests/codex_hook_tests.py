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
            "host_semantic_intent": {
                "schema": "jikuo.host_semantic_intent.v0",
                "provider": "host_ai",
                "confidence": "high",
                "work_profile": {"policy_scopes": ["editing"]},
            },
        }

        hook_input = hook.extract_hook_input(payload, {})

        self.assertEqual(hook_input.hook_event_name, "UserPromptSubmit")
        self.assertEqual(hook_input.prompt, "Please update the hook docs.")
        self.assertEqual(hook_input.cwd, ROOT / "docs")
        self.assertEqual(hook_input.session_id, "session-1")
        self.assertEqual(hook_input.turn_id, "turn-1")
        self.assertEqual(hook_input.permission_mode, "default")
        self.assertEqual(hook_input.model, "gpt-test")
        self.assertEqual(
            hook_input.host_semantic_intent["work_profile"]["policy_scopes"],
            ["editing"],
        )

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
            "semantic_intent_precondition": {
                "status": "refused",
                "user_facing_summary": "Governed editing work needs host_semantic_intent.",
                "next_actions": [
                    "classify the request and re-call JIKUO with host_semantic_intent"
                ],
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
        self.assertIn("Semantic intent precondition: refused", context)
        self.assertIn("Semantic intent required action:", context)
        self.assertIn("Host adapter contract:", context)
        self.assertIn("input_schema=jikuo.host_adapter.turn_input.v0", context)
        self.assertIn("user_turn_summary_status=provided_redacted", context)
        self.assertIn("Host semantic intent follow-up contract:", context)
        self.assertIn("after reading and understanding this turn", context)
        self.assertIn("before governed action, tool use", context)
        self.assertIn("workspace writes, or final response", context)
        self.assertIn("appropriate JIKUO router or proposal surface", context)
        self.assertIn("status=provided", context)
        self.assertIn("policy_scopes limited to discussion/editing/progress_summary", context)
        self.assertIn("requested_outcome", context)
        self.assertIn("short user_expression", context)
        self.assertIn("semantic intent coverage as degraded or missing", context)
        self.assertIn("Triggered policy count: 1.", context)
        self.assertIn("Missing evidence report count: 1.", context)
        self.assertIn("Completion receipt contract:", context)
        self.assertIn("if the host AI performs workspace writes", context)
        self.assertIn("--event completion_review", context)
        self.assertIn(f'--project-root "{ROOT}"', context)
        self.assertIn("--semantic-intent-ref", context)
        self.assertIn("anchor:turn_", context)
        self.assertIn("--inherit-semantic-intent", context)
        self.assertIn("Completion semantic evidence contract:", context)
        self.assertIn("reuses prompt-free host AI semantic intent evidence", context)
        self.assertIn("before the final response", context)
        self.assertIn("completion receipt is missing or failed", context)
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
        self.assertIn("--private-turn-input-ref-json", command)
        private_ref_json = command[command.index("--private-turn-input-ref-json") + 1]
        self.assertEqual(
            json.loads(private_ref_json)["status"],
            "available_for_private_storage",
        )
        self.assertNotIn("--user-phrase", command)
        self.assertNotIn(raw_prompt, command)

    def test_build_agent_flow_command_uses_preferred_windows_python_when_available(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: implement proof"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-python",
            turn_id="turn-python",
            permission_mode="default",
            model=None,
        )

        command = hook.build_agent_flow_command(hook_input, ROOT, "mounted", env={})

        if hook.os.name == "nt" and hook.PREFERRED_WINDOWS_PYTHON.exists():
            self.assertEqual(command[0], str(hook.PREFERRED_WINDOWS_PYTHON))
        else:
            self.assertEqual(command[0], sys.executable)

    def test_build_agent_flow_command_passes_compact_host_semantic_intent(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: implement proof"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-semantic",
            turn_id="turn-semantic",
            permission_mode="default",
            model=None,
            host_semantic_intent={
                "schema": "jikuo.host_semantic_intent.v0",
                "provider": "host_ai",
                "confidence": "high",
                "work_profile": {"policy_scopes": ["editing"]},
            },
        )

        command = hook.build_agent_flow_command(
            hook_input,
            ROOT,
            "mounted",
            env={"JIKUO_HOOK_PYTHON": "python"},
        )

        self.assertIn("--host-semantic-intent-json", command)
        semantic_json = command[command.index("--host-semantic-intent-json") + 1]
        self.assertEqual(json.loads(semantic_json)["provider"], "host_ai")
        self.assertNotIn(raw_prompt, command)

    def test_build_host_adapter_turn_input_maps_codex_payload_without_raw_prompt(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: map me into the adapter contract"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-adapter",
            turn_id="turn-adapter",
            permission_mode="default",
            model=None,
            host_semantic_intent={
                "schema": "jikuo.host_semantic_intent.v0",
                "provider": "host_ai",
                "confidence": "high",
                "work_profile": {"policy_scopes": ["editing"]},
            },
        )

        turn_input = hook.build_host_adapter_turn_input(hook_input, ROOT, "mounted")
        serialized = json.dumps(turn_input, ensure_ascii=False)

        self.assertEqual(turn_input["schema"], "jikuo.host_adapter.turn_input.v0")
        self.assertEqual(turn_input["client_id"], "codex")
        self.assertEqual(turn_input["client_event"], "UserPromptSubmit")
        self.assertEqual(turn_input["trigger_mode"], "mounted")
        self.assertEqual(turn_input["user_turn_summary"], "<redacted_user_turn>")
        self.assertEqual(turn_input["user_turn_summary_status"], "provided_redacted")
        self.assertEqual(turn_input["host_semantic_intent"]["status"], "provided")
        self.assertNotIn(raw_prompt, serialized)

    def test_execution_mode_defaults_to_in_process_with_subprocess_opt_in(self):
        hook = load_hook_module()

        self.assertEqual(hook.execution_mode_from_env({}), "in_process")
        self.assertEqual(
            hook.execution_mode_from_env({"JIKUO_HOOK_EXECUTION_MODE": "subprocess"}),
            "subprocess",
        )
        self.assertEqual(
            hook.execution_mode_from_env({"JIKUO_HOOK_EXECUTION_MODE": "cli"}),
            "subprocess",
        )

    def test_run_agent_flow_in_process_uses_agent_flow_builder_and_formatter(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: classify this turn"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-in-process",
            turn_id="turn-in-process",
            permission_mode="default",
            model=None,
            host_semantic_intent={
                "schema": "jikuo.host_semantic_intent.v0",
                "provider": "host_ai",
                "confidence": "high",
                "work_profile": {"policy_scopes": ["editing"]},
            },
        )
        calls = {}

        def fake_builder(**kwargs):
            calls["builder"] = kwargs
            return {
                "status": "review",
                "work_profile": {
                    "lifecycle_event": "conversation_turn",
                    "policy_scopes": ["editing"],
                },
            }

        def fake_formatter(proposal, *, project_root):
            calls["formatter"] = {"proposal": proposal, "project_root": project_root}
            return {
                **proposal,
                "runtime_visibility": {"last_card_ref": ".jikuo/runtime/last_card.md"},
                "client_display_links": {"links": {}},
            }

        result = hook.run_agent_flow_in_process(
            hook_input,
            ROOT,
            "mounted",
            builder=fake_builder,
            formatter=fake_formatter,
        )

        self.assertEqual(calls["builder"]["raw_event"], "conversation_turn")
        self.assertEqual(calls["builder"]["project_root"], ROOT)
        self.assertEqual(calls["builder"]["user_phrase"], raw_prompt)
        self.assertEqual(calls["builder"]["trigger_mode"], "mounted")
        self.assertEqual(calls["builder"]["host_semantic_intent"]["provider"], "host_ai")
        self.assertEqual(calls["builder"]["host_semantic_intent"]["status"], "provided")
        self.assertEqual(
            calls["builder"]["private_turn_input_ref"]["status"],
            "available_for_private_storage",
        )
        self.assertEqual(calls["formatter"]["project_root"], ROOT)
        self.assertEqual(result["runtime_visibility"]["last_card_ref"], ".jikuo/runtime/last_card.md")

    def test_run_agent_flow_in_process_handles_lone_surrogate_prompt(self):
        hook = load_hook_module()
        raw_prompt = "bad \udcaf prompt"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-in-process-surrogate",
            turn_id="turn-in-process-surrogate",
            permission_mode="default",
            model=None,
            host_semantic_intent={
                "schema": "jikuo.host_semantic_intent.v0",
                "provider": "host_ai",
                "confidence": "high",
                "work_profile": {"policy_scopes": ["editing"]},
            },
        )
        calls = {}

        def fake_builder(**kwargs):
            calls["builder"] = kwargs
            return {
                "status": "review",
                "work_profile": {
                    "lifecycle_event": "conversation_turn",
                    "policy_scopes": ["editing"],
                },
            }

        def fake_formatter(proposal, *, project_root):
            return {
                **proposal,
                "runtime_visibility": {"last_card_ref": ".jikuo/runtime/last_card.md"},
                "client_display_links": {"links": {}},
            }

        result = hook.run_agent_flow_in_process(
            hook_input,
            ROOT,
            "mounted",
            builder=fake_builder,
            formatter=fake_formatter,
        )

        self.assertEqual(calls["builder"]["user_phrase"], raw_prompt)
        self.assertEqual(
            calls["builder"]["turn_anchor"]["prompt_digest_status"],
            "hash_only",
        )
        self.assertEqual(result["status"], "review")

    def test_run_agent_flow_subprocess_accepts_structured_refusal_output(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: update docs"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-subprocess",
            turn_id="turn-subprocess",
            permission_mode="default",
            model=None,
        )
        payload = {
            "status": "refused",
            "work_profile": {
                "lifecycle_event": "conversation_turn",
                "policy_scopes": ["editing"],
            },
            "semantic_intent_precondition": {
                "status": "refused",
                "user_facing_summary": "host semantic intent required",
            },
        }
        calls = {}

        class Completed:
            returncode = 2
            stdout = json.dumps(payload)
            stderr = ""

        original_run = hook.subprocess.run

        def fake_run(command, **kwargs):
            calls["command"] = command
            calls["input"] = kwargs.get("input")
            return Completed()

        try:
            hook.subprocess.run = fake_run
            result = hook.run_agent_flow_subprocess(
                hook_input,
                ROOT,
                "mounted",
                env={"JIKUO_HOOK_PYTHON": "python"},
            )
        finally:
            hook.subprocess.run = original_run

        self.assertEqual(result["status"], "refused")
        self.assertEqual(calls["input"], raw_prompt)
        self.assertNotIn(raw_prompt, calls["command"])

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
                    "basis": {
                        "host_semantic_intent": {
                            "status": "provided",
                            "provider": "host_ai",
                        }
                    },
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
        self.assertIn("Semantic intent status: provided.", additional_context)
        self.assertIn("Host adapter contract:", additional_context)
        self.assertIn("JIKUO remains the final work-profile", additional_context)
        self.assertIn("Completion receipt contract:", additional_context)
        self.assertIn("--event completion_review", additional_context)
        self.assertIn("--inherit-semantic-intent", additional_context)
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

    def test_main_handles_lone_surrogate_prompt_without_degrading(self):
        hook = load_hook_module()
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "bad \udcaf prompt",
            "cwd": str(ROOT),
            "session_id": "session-surrogate",
            "turn_id": "turn-surrogate",
            "permission_mode": "default",
        }

        def fake_runner(hook_input, project_root, trigger_mode):
            self.assertEqual(hook_input.prompt, payload["prompt"])
            return {
                "runtime_visibility": {
                    "last_card_ref": ".jikuo/runtime/last_card.md",
                },
                "work_profile": {
                    "lifecycle_event": "conversation_turn",
                    "policy_scopes": ["editing"],
                    "basis": {
                        "host_semantic_intent": {
                            "status": "provided",
                            "provider": "host_ai",
                        }
                    },
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
        self.assertNotIn("systemMessage", output)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("JIKUO mounted pre-turn ran", additional_context)
        self.assertIn("prompt_digest=hash_only", additional_context)
        self.assertNotIn(payload["prompt"], additional_context)

    def test_main_escapes_lone_surrogate_in_failure_context(self):
        hook = load_hook_module()
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "safe prompt",
            "cwd": str(ROOT),
            "session_id": "session-surrogate-failure",
            "turn_id": "turn-surrogate-failure",
            "permission_mode": "default",
        }

        def failing_runner(hook_input, project_root, trigger_mode):
            raise hook.HookExecutionError("bad display \udcaf")

        stdout = io.StringIO()
        exit_code = hook.main(
            stdin=io.StringIO(json.dumps(payload)),
            stdout=stdout,
            runner=failing_runner,
            env={},
        )

        self.assertEqual(exit_code, 0)
        output = json.loads(stdout.getvalue())
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("bad display \\udcaf", additional_context)
        self.assertNotIn("\udcaf", additional_context)

    def test_failure_context_redacts_prompt_echo_from_errors(self):
        hook = load_hook_module()
        raw_prompt = "SECRET_PROMPT_VALUE: do not leak me"
        hook_input = hook.HookInput(
            hook_event_name="UserPromptSubmit",
            prompt=raw_prompt,
            cwd=ROOT,
            session_id="session-redact",
            turn_id="turn-redact",
            permission_mode="default",
            model=None,
        )

        context = hook.render_failure_context(
            hook.HookExecutionError(f"boom {raw_prompt}"),
            hook_input,
            ROOT,
        )

        self.assertIn("<REDACTED_PROMPT_ECHO>", context)
        self.assertNotIn(raw_prompt, context)


if __name__ == "__main__":
    unittest.main()
