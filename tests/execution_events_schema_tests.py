import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "src" / "jikuo" / "fixtures" / "events"

SCHEMA = "jikuo.execution_event.v0_draft"
EVENT_TYPES = {
    "jikuo.execution_started",
    "jikuo.conversation_turn_routed",
    "jikuo.policy_runtime_evaluated",
    "jikuo.guarded_write_refused",
    "jikuo.guarded_write_applied",
    "jikuo.adapter_degraded",
    "jikuo.execution_completed",
}
PRIVACY_CLASSES = {"return", "local_only", "redact_required", "redact_optional"}


def iter_events():
    for path in sorted(FIXTURE_DIR.glob("example_*.jsonl")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip():
                yield path, line_no, json.loads(line)


class ExecutionEventsSchemaTests(unittest.TestCase):
    def test_fixture_directory_exists(self) -> None:
        self.assertTrue(FIXTURE_DIR.is_dir())

    def test_required_envelope_fields(self) -> None:
        events = list(iter_events())
        self.assertGreaterEqual(len(events), 8)
        for path, line_no, event in events:
            with self.subTest(path=path.name, line=line_no):
                self.assertEqual(event["schema"], SCHEMA)
                self.assertIn(event["event_type"], EVENT_TYPES)
                self.assertIsInstance(event["event_id"], str)
                self.assertIsInstance(event["run_id"], str)
                self.assertIsInstance(event["monotonic_seq"], int)
                self.assertRegex(event["wall_clock_utc"], r"^\d{4}-\d{2}-\d{2}T")
                self.assertIn(event["source_surface"], {"cli", "mcp", "adapter", "hook", "studio", "test_fixture"})
                self.assertIsInstance(event["field_classification"], dict)
                self.assertIsInstance(event["payload"], dict)

    def test_privacy_classification_values(self) -> None:
        for path, line_no, event in iter_events():
            for field, privacy_class in event["field_classification"].items():
                with self.subTest(path=path.name, line=line_no, field=field):
                    self.assertIn(privacy_class, PRIVACY_CLASSES)

    def test_run_monotonic_sequence(self) -> None:
        by_file_and_run: dict[tuple[str, str], list[int]] = {}
        for path, _line_no, event in iter_events():
            by_file_and_run.setdefault((path.name, event["run_id"]), []).append(event["monotonic_seq"])
        for (file_name, run_id), seqs in by_file_and_run.items():
            with self.subTest(file=file_name, run_id=run_id):
                self.assertEqual(seqs, sorted(seqs))
                self.assertEqual(len(seqs), len(set(seqs)))

    def test_no_raw_transcript_or_unredacted_approval_phrase(self) -> None:
        serialized = "\n".join(json.dumps(event, ensure_ascii=False) for _p, _l, event in iter_events())
        self.assertNotIn("raw_chat_transcript", serialized)
        self.assertNotIn("I approve", serialized)
        self.assertNotIn("approval settings for", serialized)


if __name__ == "__main__":
    unittest.main()
