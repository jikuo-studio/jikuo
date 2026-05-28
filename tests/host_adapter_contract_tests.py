import json
import unittest

from jikuo.integrations import host_adapter_contract


class HostAdapterContractTests(unittest.TestCase):
    def test_turn_input_redacts_raw_prompt_and_preserves_compact_semantic_intent(self):
        raw_prompt = "SECRET_HOST_ADAPTER_PROMPT: update the hook docs and summarize meaning"
        normalized = host_adapter_contract.normalize_turn_input(
            {
                "client_id": "codex",
                "client_event": "UserPromptSubmit",
                "project_root": "D:/personal_project/Jikuo",
                "session_id": "session-1",
                "turn_id": "turn-1",
                "trigger_mode": "mounted",
                "prompt": raw_prompt,
                "host_semantic_intent": {
                    "schema": "jikuo.host_semantic_intent.v0",
                    "provider": "host_ai",
                    "confidence": "high",
                    "work_profile": {"policy_scopes": ["editing"]},
                    "intent_slices": [
                        {
                            "id": "update_docs",
                            "user_expression": "update hook docs",
                            "policy_scopes": ["editing"],
                        }
                    ],
                },
            }
        )

        serialized = json.dumps(normalized, ensure_ascii=False)
        self.assertEqual(normalized["schema"], host_adapter_contract.HOST_ADAPTER_TURN_INPUT_SCHEMA)
        self.assertEqual(normalized["client_id"], "codex")
        self.assertEqual(normalized["trigger_mode"], "mounted")
        self.assertEqual(normalized["user_turn_summary"], host_adapter_contract.REDACTED_USER_TURN)
        self.assertEqual(normalized["user_turn_summary_status"], "provided_redacted")
        self.assertEqual(normalized["host_semantic_intent"]["status"], "provided")
        self.assertEqual(normalized["host_semantic_intent"]["policy_scopes"], ["editing"])
        self.assertNotIn(raw_prompt, serialized)

    def test_turn_input_accepts_compact_summary_without_raw_prompt(self):
        normalized = host_adapter_contract.normalize_turn_input(
            {
                "client_id": "vscode-copilot",
                "client_event": "extension.preTurn",
                "user_turn_summary": "update hook docs and explain business meaning",
                "trigger_mode": "mounted",
            }
        )

        self.assertEqual(normalized["client_id"], "vscode_copilot")
        self.assertEqual(normalized["user_turn_summary_status"], "provided_compact")
        self.assertEqual(
            normalized["user_turn_summary"],
            "update hook docs and explain business meaning",
        )
        self.assertEqual(normalized["host_semantic_intent"]["status"], "unavailable")

    def test_turn_result_redacts_prompt_echo_from_failure_summary(self):
        raw_prompt = "SECRET_HOST_ADAPTER_PROMPT: configure the adapter"
        normalized = host_adapter_contract.normalize_turn_result(
            {
                "status": "degraded",
                "semantic_intent_status": "unavailable",
                "prompt": raw_prompt,
                "failure_summary": f"hook failed while handling {raw_prompt}",
                "card_links": ["[last_card.md](D:/x/.jikuo/runtime/last_card.md)"],
                "next_required_actions": ["retry with visible degradation"],
            }
        )

        serialized = json.dumps(normalized, ensure_ascii=False)
        self.assertEqual(normalized["status"], "degraded")
        self.assertTrue(normalized["privacy"]["failure_summary_redacted"])
        self.assertIn(host_adapter_contract.REDACTED_PROMPT_ECHO, serialized)
        self.assertNotIn(raw_prompt, serialized)

    def test_codex_current_path_is_explicit_about_remaining_provider_gap(self):
        path = host_adapter_contract.codex_current_project_hook_path()

        self.assertEqual(path["current_path"], "project_local_user_prompt_submit_hook")
        self.assertIn("in_process_jikuo_invocation", path["accepted_capabilities"])
        self.assertEqual(
            path["semantic_provider_status"],
            "unavailable_until_wrapper_plugin_or_sampling_provider",
        )
        self.assertIn(
            "does_not_claim_host_time_ai_semantic_routing_is_accepted",
            path["non_effects"],
        )


if __name__ == "__main__":
    unittest.main()
