import importlib.util
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "task_session.py"
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
READY_PROJECT = FIXTURES / "task_session_ready_project"
MISSING_PROJECT = FIXTURES / "missing_project"
TEMP_ROOT = ROOT / "tmp" / "jikuo_task_session_tests"


@contextmanager
def temp_project_dir():
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield str(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)


def create_ready_project(temp_dir: str, project_root_value: str | None = None) -> Path:
    root = Path(temp_dir)
    registry = root / "docs" / "scenarios" / "interactive_novel" / "governance"
    registry.mkdir(parents=True)
    (registry / "rule_registry.yaml").write_text("rules: []\n", encoding="utf-8")
    state_root = root / ".jikuo"
    state_root.mkdir()
    state_project_root = project_root_value or str(root)
    (state_root / "project_state.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.project_local_state.v0"',
                'project_id: "temp_project"',
                f'project_root: "{state_project_root}"',
                f'jikuo_state_root: "{state_root}"',
                "active_scenario_packages:",
                '  - "engineering_governance"',
                "accepted_contract_refs:",
                '  - "docs/jikuo/schemas/task_session.schema.md"',
                'registry_ref: "docs/scenarios/interactive_novel/governance/rule_registry.yaml"',
                "latest_task_session_refs: []",
                "latest_rule_proposal_refs: []",
                "latest_handoff_ref: null",
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return root


def append_project_state_text(project_root: Path, text: str) -> None:
    state_file = project_root / ".jikuo" / "project_state.yaml"
    state_file.write_text(
        state_file.read_text(encoding="utf-8") + text,
        encoding="utf-8",
    )


def load_task_session_module():
    spec = importlib.util.spec_from_file_location("task_session", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load task_session module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TaskSessionHelperTests(unittest.TestCase):
    def test_start_plan_requires_initialized_project_state(self):
        module = load_task_session_module()
        plan = module.build_start_plan(
            project_root=MISSING_PROJECT,
            task_title="Task Session Probe",
            created_at="2026-05-04T00:00:00Z",
        )

        self.assertFalse(plan["can_start"])
        self.assertIsNone(plan["would_create"])
        self.assertIn("project state must be initialized", plan["warnings"][0])
        self.assertFalse((MISSING_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_start_dry_run_builds_structured_record_without_writing(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "start",
                "--dry-run",
                "--task-title",
                "Task Session Probe",
                "--project-root",
                str(READY_PROJECT),
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
        plan = json.loads(completed.stdout)
        self.assertEqual(plan["schema"], "jikuo.task_session_start_plan.v0")
        self.assertTrue(plan["report_only"])
        self.assertTrue(plan["can_start"])
        self.assertFalse(plan["write_allowed_by_command"])
        self.assertIn("pkg://jikuo/schemas/task_session.schema.md", plan["source_refs"])
        self.assertEqual(plan["would_create"]["schema"], "jikuo.task_session.v0")
        self.assertEqual(
            plan["would_create"]["capture_policy"]["raw_chat_transcript"],
            "disallowed",
        )
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_start_without_dry_run_is_rejected(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "start",
                "--task-title",
                "Task Session Probe",
                "--project-root",
                str(READY_PROJECT),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("requires --dry-run or --write", completed.stderr)
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_write_requires_confirmation_and_approval(self):
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "start",
                    "--write",
                    "--task-title",
                    "Task Session Probe",
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["schema"], "jikuo.task_session_write_result.v0")
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_write_creates_session_file_without_project_state_index_update(self):
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "start",
                    "--write",
                    "--confirm-create-task-session",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--task-title",
                    "Task Session Probe",
                    "--project-root",
                    str(project_root),
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
            result = json.loads(completed.stdout)
            self.assertEqual(result["schema"], "jikuo.task_session_write_result.v0")
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertTrue(result["created_file"])
            self.assertFalse(result["updated_project_state_index"])
            session_path = Path(result["session_path"])
            self.assertTrue(session_path.exists())
            text = session_path.read_text(encoding="utf-8")
            self.assertIn('schema: "jikuo.task_session.v0"', text)
            self.assertIn("raw_chat_transcript: \"disallowed\"", text)

            state_text = (project_root / ".jikuo" / "project_state.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn("latest_task_session_refs: []", state_text)
            self.assertNotIn(str(session_path), state_text)

            status = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "status",
                    "--session-id",
                    result["session_id"],
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            status_result = json.loads(status.stdout)
            self.assertEqual(status_result["session_status"], "found")
            self.assertEqual(
                status_result["matched_records"][0]["schema"],
                "jikuo.task_session.v0",
            )
            self.assertEqual(
                status_result["matched_records"][0]["session_id"],
                result["session_id"],
            )

    def test_write_refuses_existing_session_file_collision(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            first, first_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            second, second_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )

            self.assertEqual(first_code, 0, first)
            self.assertEqual(second_code, 2, second)
            self.assertEqual(second["status"], "refused")
            self.assertIn("session_id_collision", second["refusal_reasons"])
            self.assertEqual(
                len(list((project_root / ".jikuo" / "task_sessions").glob("*.yaml"))),
                1,
            )

    def test_write_refuses_project_root_mismatch(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir, project_root_value="fixture")
            result, code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )

            self.assertEqual(code, 2, result)
            self.assertEqual(result["status"], "refused")
            self.assertIn("project_root_mismatch", result["refusal_reasons"])
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_index_dry_run_no_sessions_does_not_write(self):
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "index",
                    "--dry-run",
                    "--project-root",
                    str(project_root),
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
            plan = json.loads(completed.stdout)
            self.assertEqual(
                plan["schema"], "jikuo.task_session_index_refresh_plan.v0"
            )
            self.assertEqual(plan["discovered_session_count"], 0)
            self.assertFalse(plan["would_update_project_state"])
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())
            self.assertIn(
                "latest_task_session_refs: []",
                (project_root / ".jikuo" / "project_state.yaml").read_text(
                    encoding="utf-8"
                ),
            )

    def test_index_dry_run_discovers_written_session_without_writing_index(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            plan = module.build_index_refresh_plan(project_root=project_root)

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(plan["discovered_session_count"], 1)
            self.assertTrue(plan["would_update_project_state"])
            self.assertEqual(
                plan["proposed_latest_task_session_refs"][0]["session_id"],
                write_result["session_id"],
            )
            state_text = (project_root / ".jikuo" / "project_state.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn("latest_task_session_refs: []", state_text)
            self.assertNotIn(write_result["session_id"], state_text)

    def test_index_refresh_requires_confirmation_and_approval(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "index",
                    "--refresh",
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(completed.returncode, 2, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(
                result["schema"], "jikuo.task_session_index_refresh_result.v0"
            )
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["updated_project_state_index"])
            self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])

    def test_index_refresh_updates_project_state_without_creating_sessions(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            before_files = sorted(
                path.name
                for path in (project_root / ".jikuo" / "task_sessions").glob("*.yaml")
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "index",
                    "--refresh",
                    "--confirm-update-project-state-index",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            after_files = sorted(
                path.name
                for path in (project_root / ".jikuo" / "task_sessions").glob("*.yaml")
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "updated")
            self.assertTrue(result["updated_project_state_index"])
            self.assertEqual(before_files, after_files)
            state_text = (project_root / ".jikuo" / "project_state.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn(write_result["session_id"], state_text)
            self.assertIn(".jikuo/task_sessions/", state_text)
            self.assertIn("latest_rule_proposal_refs: []", state_text)

    def test_index_refresh_no_change_after_indexed(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            first, first_code = module.refresh_task_session_index(
                project_root=project_root,
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            second, second_code = module.refresh_task_session_index(
                project_root=project_root,
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(first_code, 0, first)
            self.assertEqual(second_code, 0, second)
            self.assertEqual(first["status"], "updated")
            self.assertEqual(second["status"], "no_change")
            self.assertFalse(second["updated_project_state_index"])

    def test_index_refresh_refuses_duplicate_session_ids(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            original = Path(write_result["session_path"])
            duplicate = original.with_name(f"duplicate_{original.name}")
            shutil.copyfile(original, duplicate)
            result, code = module.refresh_task_session_index(
                project_root=project_root,
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(code, 2, result)
            self.assertEqual(result["status"], "refused")
            self.assertIn("duplicate_session_id", result["refusal_reasons"])
            state_text = (project_root / ".jikuo" / "project_state.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn("latest_task_session_refs: []", state_text)

    def test_index_refresh_preserves_unknown_project_state_fields(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            append_project_state_text(project_root, 'custom_field: "keep me"\n')
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            result, code = module.refresh_task_session_index(
                project_root=project_root,
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(code, 0, result)
            state_text = (project_root / ".jikuo" / "project_state.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn('custom_field: "keep me"', state_text)
            self.assertIn(write_result["session_id"], state_text)

    def test_update_dry_run_selects_session_without_writing(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            before_text = Path(write_result["session_path"]).read_text(encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "update",
                    "--dry-run",
                    "--session-id",
                    write_result["session_id"],
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            after_text = Path(write_result["session_path"]).read_text(encoding="utf-8")

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            plan = json.loads(completed.stdout)
            self.assertEqual(plan["schema"], "jikuo.task_session_update_plan.v0")
            self.assertEqual(plan["patch_kind"], "inspect")
            self.assertFalse(plan["would_update_task_session"])
            self.assertEqual(before_text, after_text)

    def test_update_append_evidence_requires_confirmation_and_approval(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "update",
                    "--append-evidence",
                    "--session-id",
                    write_result["session_id"],
                    "--evidence-kind",
                    "checker",
                    "--evidence-ref",
                    "tools/jikuo/task_session_tests.py",
                    "--summary",
                    "Lifecycle evidence probe",
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(completed.returncode, 2, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["schema"], "jikuo.task_session_update_result.v0")
            self.assertEqual(result["status"], "refused")
            self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])

    def test_update_append_evidence_and_verification_are_append_only(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            evidence_result, evidence_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="evidence",
                summary="Lifecycle evidence probe",
                evidence_kind="checker",
                evidence_ref="tools/jikuo/task_session_tests.py",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
                created_at="2026-05-04T00:10:00Z",
            )
            verification_result, verification_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="verification",
                summary="Lifecycle verification probe",
                command_name="python -B tools/jikuo/task_session_tests.py",
                exit_code=0,
                verification_layer="unit",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
                created_at="2026-05-04T00:20:00Z",
            )
            text = Path(write_result["session_path"]).read_text(encoding="utf-8")

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(evidence_code, 0, evidence_result)
            self.assertEqual(verification_code, 0, verification_result)
            self.assertIn("evidence_snapshots:", text)
            self.assertIn("Lifecycle evidence probe", text)
            self.assertIn("verification:", text)
            self.assertIn("Lifecycle verification probe", text)
            self.assertIn("latest_task_session_refs: []", (project_root / ".jikuo" / "project_state.yaml").read_text(encoding="utf-8"))

    def test_complete_accepted_requires_user_decision(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            result, code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="completion",
                summary="Ready to accept",
                completion_status="accepted",
                confirmed=True,
                approval_phrase=None,
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(code, 2, result)
            self.assertIn("accepted_completion_requires_user_decision", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])

    def test_complete_and_handoff_update_target_session_only(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            complete_result, complete_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="completion",
                summary="Implementation accepted for review.",
                completion_status="accepted",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
                created_at="2026-05-04T00:30:00Z",
            )
            handoff_result, handoff_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="handoff",
                summary="Next agent should continue from TASKSESSION-04.",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
                created_at="2026-05-04T00:40:00Z",
            )
            text = Path(write_result["session_path"]).read_text(encoding="utf-8")

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(complete_code, 0, complete_result)
            self.assertEqual(handoff_code, 0, handoff_result)
            self.assertIn("status: \"accepted\"", text)
            self.assertIn("lifecycle_status: \"accepted\"", text)
            self.assertIn("Implementation accepted for review.", text)
            self.assertIn("Next agent should continue from TASKSESSION-04.", text)
            self.assertIn("user_decisions:", text)

    def test_terminal_session_refuses_late_evidence(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            complete_result, complete_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="completion",
                summary="Accepted.",
                completion_status="accepted",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            late_result, late_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="evidence",
                summary="Late evidence",
                evidence_kind="checker",
                evidence_ref="tools/jikuo/task_session_tests.py",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(complete_code, 0, complete_result)
            self.assertEqual(late_code, 2, late_result)
            self.assertIn("terminal_session_update_disallowed", late_result["refusal_reasons"])

    def test_update_refuses_duplicate_or_raw_chat_session_update(self):
        module = load_task_session_module()
        with temp_project_dir() as temp_dir:
            project_root = create_ready_project(temp_dir)
            write_result, write_code = module.write_task_session(
                project_root=project_root,
                task_title="Task Session Probe",
                owner_agent="codex",
                created_at="2026-05-04T00:00:00Z",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            raw_result, raw_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="evidence",
                summary="raw chat transcript dump",
                evidence_kind="checker",
                evidence_ref="tools/jikuo/task_session_tests.py",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )
            duplicate = Path(write_result["session_path"]).with_name(
                f"duplicate_{Path(write_result['session_path']).name}"
            )
            shutil.copyfile(Path(write_result["session_path"]), duplicate)
            duplicate_result, duplicate_code = module.update_task_session(
                project_root=project_root,
                session_id=write_result["session_id"],
                patch_kind="evidence",
                summary="Lifecycle evidence probe",
                evidence_kind="checker",
                evidence_ref="tools/jikuo/task_session_tests.py",
                confirmed=True,
                approval_phrase="<exact user phrase as spoken>",
            )

            self.assertEqual(write_code, 0, write_result)
            self.assertEqual(raw_code, 2, raw_result)
            self.assertIn("raw_chat_transcript_disallowed", raw_result["refusal_reasons"])
            self.assertEqual(duplicate_code, 2, duplicate_result)
            self.assertIn("multiple_session_matches", duplicate_result["refusal_reasons"])

    def test_empty_task_title_yields_warning_in_plan(self):
        module = load_task_session_module()
        plan = module.build_start_plan(
            project_root=READY_PROJECT,
            task_title=" ",
            created_at="2026-05-04T00:00:00Z",
        )

        self.assertFalse(plan["can_start"])
        self.assertIn("task title is required", plan["warnings"])

    def test_status_reports_not_found_without_writing(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "status",
                "--session-id",
                "task_missing_session_00000000",
                "--project-root",
                str(READY_PROJECT),
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
        status = json.loads(completed.stdout)
        self.assertEqual(status["schema"], "jikuo.task_session_status.v0")
        self.assertEqual(status["session_status"], "not_found")
        self.assertFalse(status["write_allowed_by_command"])
        self.assertEqual(status["matched_records"], [])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_text_output_keeps_no_write_signal(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "start",
                "--dry-run",
                "--task-title",
                "Task Session Probe",
                "--project-root",
                str(READY_PROJECT),
                "--format",
                "text",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("JIKUO Task Session Start Plan (dry-run)", completed.stdout)
        self.assertIn("Writes performed: no", completed.stdout)
        self.assertIn("Write allowed by command: no", completed.stdout)


if __name__ == "__main__":
    unittest.main()
