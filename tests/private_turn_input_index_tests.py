import json
import tempfile
import unittest
from pathlib import Path

from jikuo import private_turn_input_index, turn_anchor


class PrivateTurnInputIndexTests(unittest.TestCase):
    def test_append_requires_explicit_raw_input_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            raw_prompt = "SECRET_PRIVATE_INDEX_PROMPT: do not persist by accident"
            anchor = turn_anchor.build_turn_anchor(
                session_id="session-refused",
                turn_id="turn-refused",
                raw_prompt=raw_prompt,
            )

            report = private_turn_input_index.append_turn_input_record(
                project_root=project_root,
                raw_user_input=raw_prompt,
                turn_anchor=anchor,
            )

            self.assertEqual(report["status"], "refused")
            self.assertFalse(report["write_performed"])
            self.assertFalse(
                (project_root / ".jikuo" / "private" / "turn_inputs.jsonl").exists()
            )

    def test_private_index_stores_raw_prompt_but_public_refs_do_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            raw_prompt = "SECRET_PRIVATE_INDEX_PROMPT: find my execution evidence"
            anchor = turn_anchor.build_turn_anchor(
                client_id="codex",
                client_event="UserPromptSubmit",
                session_id="session-index",
                turn_id="turn-index",
                raw_prompt=raw_prompt,
            )
            semantic = {
                "schema": "jikuo.host_semantic_intent.v0",
                "status": "provided",
                "provider": "host_ai",
                "policy_scopes": ["editing"],
                "turn_anchor": anchor,
            }

            report = private_turn_input_index.append_turn_input_record(
                project_root=project_root,
                raw_user_input=raw_prompt,
                turn_anchor=anchor,
                host_semantic_intent=semantic,
                source_client="codex",
                source_event="UserPromptSubmit",
                task_start_refs=[".jikuo/runtime/history/task_start.md"],
                completion_review_refs=[".jikuo/runtime/history/completion.md"],
                confirm_store_raw_input=True,
                approval_phrase="store this raw input privately",
            )
            serialized_public = json.dumps(report, ensure_ascii=False)

            self.assertEqual(report["status"], "ok")
            self.assertTrue(report["write_performed"])
            self.assertNotIn(raw_prompt, serialized_public)
            self.assertEqual(
                report["private_turn_input_ref"]["index_ref"],
                ".jikuo/private/turn_inputs.jsonl",
            )
            index_path = project_root / ".jikuo" / "private" / "turn_inputs.jsonl"
            self.assertTrue(index_path.is_file())
            self.assertTrue((project_root / ".jikuo" / "private" / ".gitignore").is_file())
            self.assertIn(raw_prompt, index_path.read_text(encoding="utf-8"))

            public_records = private_turn_input_index.read_private_records(
                project_root=project_root,
            )
            raw_records = private_turn_input_index.read_private_records(
                project_root=project_root,
                include_raw=True,
            )
            self.assertNotIn(raw_prompt, json.dumps(public_records, ensure_ascii=False))
            self.assertIn(raw_prompt, json.dumps(raw_records, ensure_ascii=False))

            search = private_turn_input_index.search_private_turn_inputs(
                project_root=project_root,
                query_text="execution evidence",
            )
            self.assertEqual(search["search_mode"], "literal_private_index")
            self.assertEqual(search["match_count"], 1)
            self.assertFalse(search["privacy"]["raw_prompt_returned"])
            self.assertNotIn(raw_prompt, json.dumps(search, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
