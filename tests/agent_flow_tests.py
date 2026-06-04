import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "agent_flow.py"
POLICY_STORE_TOOL = ROOT / "src" / "jikuo" / "policy_store.py"
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
READY_PROJECT = FIXTURES / "task_session_ready_project"
MISSING_PROJECT = FIXTURES / "missing_project"
POLICY_ACTIVE_PROJECT = FIXTURES / "policy_store_active_project"
POLICY_EVIDENCE_SESSION_PROJECT = FIXTURES / "policy_evidence_session_project"
POLICY_EVIDENCE_INGEST_PROJECT = FIXTURES / "policy_store_evidence_project"
POLICY_CONDITION_PROJECT = FIXTURES / "policy_store_condition_project"
POLICY_REAL_CHAIN_PROJECT = FIXTURES / "policy_store_real_chain_testing_project"
POLICY_TEMPLATE = (
    ROOT
    / "src"
    / "jikuo"
    / "policy_templates"
    / "engineering_governance"
    / "POLICYTEMPLATE-local-policy-task-scope-control-before-packaging.yaml"
)


def require_git() -> None:
    if shutil.which("git") is None:
        raise unittest.SkipTest("git executable is not available")


def run_git(project_root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(project_root), "-c", "core.excludesFile=", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def initialize_git_repo(project_root: Path) -> None:
    require_git()
    run_git(project_root, "init")
    run_git(project_root, "config", "user.name", "JIKUO Test")
    run_git(project_root, "config", "user.email", "jikuo-test@example.com")


def commit_project_baseline(project_root: Path) -> None:
    run_git(project_root, "add", ".")
    run_git(project_root, "commit", "-m", "baseline")


def create_agent_flow_ready_project(root: Path) -> None:
    registry = root / "docs" / "governance"
    registry.mkdir(parents=True, exist_ok=True)
    (registry / "rule_registry.yaml").write_text("rules: []\n", encoding="utf-8")
    state_root = root / ".jikuo"
    state_root.mkdir(parents=True, exist_ok=True)
    (state_root / "project_state.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.project_local_state.v0"',
                'project_id: "agent_flow_ready_project"',
                f'project_root: "{root}"',
                f'jikuo_state_root: "{state_root}"',
                "active_scenario_packages:",
                '  - "engineering_governance"',
                "accepted_contract_refs:",
                '  - "pkg://jikuo/schemas/task_session.schema.md"',
                'registry_ref: "docs/governance/rule_registry.yaml"',
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


def add_policy_work_profile_applicability(policy_path: Path) -> None:
    text = policy_path.read_text(encoding="utf-8")
    text = text.replace(
        "triggers:\n",
        "\n".join(
            [
                "applies_to_work_profile:",
                '  - lifecycle_events: ["completion_review"]',
                '    policy_scopes: ["progress_summary"]',
                '    operation_classes: ["no_tool"]',
                "triggers:",
                "",
            ]
        ),
        1,
    )
    policy_path.write_text(text, encoding="utf-8")


def add_matching_policy_work_profile_applicability(policy_path: Path) -> None:
    text = policy_path.read_text(encoding="utf-8")
    text = text.replace(
        "triggers:\n",
        "\n".join(
            [
                "applies_to_work_profile:",
                '  - lifecycle_events: ["task_start"]',
                '    policy_scopes: ["editing"]',
                '    operation_classes: ["write_file"]',
                "triggers:",
                "",
            ]
        ),
        1,
    )
    policy_path.write_text(text, encoding="utf-8")


def write_agent_flow_project_context(root: Path) -> None:
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "latest.md").write_text("latest", encoding="utf-8")
    (docs_dir / "previous.md").write_text("previous", encoding="utf-8")
    context_path = root / ".jikuo" / "project_context.yaml"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.project_context.v0"',
                "project:",
                '  project_id: "agent_flow_template_import_fixture"',
                '  project_type: "test"',
                '  project_root_policy: "bindings_must_resolve_inside_project_root"',
                "document_roles:",
                "  latest_todo_map:",
                '    path: "docs/latest.md"',
                "    required: true",
                "  previous_todo_map:",
                '    path: "docs/previous.md"',
                "    required: true",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_agent_flow_document_mount_project_context(root: Path) -> None:
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "governance.md").write_text("governance", encoding="utf-8")
    (docs_dir / "required.md").write_text("required", encoding="utf-8")
    (docs_dir / "main.md").write_text("main", encoding="utf-8")
    context_path = root / ".jikuo" / "project_context.yaml"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.project_context.v0"',
                "project:",
                '  project_id: "agent_flow_artifact_assurance_fixture"',
                '  project_type: "test"',
                '  project_root_policy: "bindings_must_resolve_inside_project_root"',
                "document_roles:",
                "  required_context:",
                '    path: "docs/required.md"',
                "    required: true",
                "main_document_mounts:",
                "  active_mount_authority:",
                '    - ".jikuo/project_context.yaml"',
                '    - "docs/governance.md"',
                "  checked_before_slice_completion:",
                '    - path: "docs/main.md"',
                '      update_required_when: "runtime assurance card projection changes"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_taskmap_distinction_policy_store(root: Path) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    (approved / "POLICY-jikuo-taskmap-insight-followup-distinction.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                'policy_id: "POLICY-jikuo-taskmap-insight-followup-distinction"',
                "version: 1",
                'status: "active_report_only"',
                'title: "Taskmap insight follow-up distinction in user summaries"',
                'scenario_package: "engineering_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                '    ref: "tests:taskmap_distinction_policy"',
                "triggers:",
                '  - trigger_id: "TRG-task-start"',
                '    type: "task_lifecycle_event"',
                '    event: "task_start"',
                "conditions:",
                "  []",
                "required_actions:",
                '  - action_id: "ACT-distinguish-taskmap-insights-followups-in-user-summary"',
                '    type: "distinguish_taskmap_insights_followups_in_user_summary"',
                "required_evidence:",
                '  - evidence_id: "EVD-taskmap-insight-followup-distinction-evidence"',
                '    type: "taskmap_insight_followup_distinction_evidence"',
                '    satisfies_action: "ACT-distinguish-taskmap-insights-followups-in-user-summary"',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "agent_flow_taskmap_distinction_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                '  - policy_id: "POLICY-jikuo-taskmap-insight-followup-distinction"',
                "    version: 1",
                '    path: ".jikuo/policies/approved/POLICY-jikuo-taskmap-insight-followup-distinction.yaml"',
                "proposal_refs:",
                "  []",
                "deprecated_policy_refs:",
                "  []",
                "superseded_policy_refs:",
                "  []",
                'last_updated_at: "2026-05-14T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_self_bootstrap_mcp_user_boundary_policy_store(root: Path) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    policy_id = "POLICY-jikuo-self-bootstrap-mcp-user-boundary"
    (approved / f"{policy_id}.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                f'policy_id: "{policy_id}"',
                "version: 1",
                'status: "active_report_only"',
                'title: "JIKUO self-bootstrap MCP user boundary"',
                'scenario_package: "engineering_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                '    ref: "tests:self_bootstrap_mcp_user_boundary"',
                "triggers:",
                '  - trigger_id: "TRG-task-start"',
                '    type: "task_lifecycle_event"',
                '    event: "task_start"',
                "conditions:",
                '  - condition_id: "COND-task-type"',
                '    type: "task_type_is"',
                '    value: "jikuo_development"',
                '  - condition_id: "COND-jikuo-layer"',
                '    type: "jikuo_layer_is"',
                '    value: "policy_governance"',
                '  - condition_id: "COND-changed-path"',
                '    type: "changed_path_matches"',
                '    pattern: "**"',
                '  - condition_id: "COND-added-path"',
                '    type: "added_path_matches"',
                '    pattern: "**"',
                "required_actions:",
                '  - action_id: "ACT-use-mcp-path-or-core-debug"',
                '    type: "use_mcp_path_for_governed_jikuo_work_or_explicitly_label_core_debug"',
                "required_evidence:",
                '  - evidence_id: "EVD-jikuo-mcp-or-core-debug-path-evidence"',
                '    type: "jikuo_mcp_or_core_debug_path_evidence"',
                '    satisfies_action: "ACT-use-mcp-path-or-core-debug"',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "agent_flow_self_bootstrap_mcp_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{policy_id}"',
                "    version: 1",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
                "proposal_refs:",
                "  []",
                "deprecated_policy_refs:",
                "  []",
                "superseded_policy_refs:",
                "  []",
                'last_updated_at: "2026-05-28T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_conversation_policy_suggestion_store(root: Path) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    policy_id = "POLICY-jikuo-conversation-level-proactive-policy-suggestion"
    (approved / f"{policy_id}.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                f'policy_id: "{policy_id}"',
                "version: 1",
                'status: "active_report_only"',
                'title: "Conversation-level proactive policy suggestion from user interaction patterns"',
                'scenario_package: "engineering_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                '    ref: "tests:conversation_policy_suggestion"',
                "applies_to_work_profile:",
                '  - lifecycle_events: ["conversation_turn"]',
                '    policy_scopes: ["discussion", "editing", "progress_summary"]',
                "triggers:",
                '  - trigger_id: "TRG-conversation-turn"',
                '    type: "task_lifecycle_event"',
                '    event: "conversation_turn"',
                "conditions:",
                "  []",
                "required_actions:",
                '  - action_id: "ACT-review-repeated-user-interaction-patterns-for-policy-candidates"',
                '    type: "review_repeated_user_interaction_patterns_for_policy_candidates"',
                "required_evidence:",
                '  - evidence_id: "EVD-proactive-policy-suggestion-review-evidence"',
                '    type: "proactive_policy_suggestion_review_evidence"',
                '    satisfies_action: "ACT-review-repeated-user-interaction-patterns-for-policy-candidates"',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "agent_flow_conversation_policy_suggestion_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{policy_id}"',
                "    version: 1",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
                "proposal_refs: []",
                "deprecated_policy_refs: []",
                "superseded_policy_refs: []",
                'last_updated_at: "2026-05-16T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_semantic_scope_distribution_policy_store(root: Path) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    policy_ids = [
        "POLICY-jikuo-first-principles-critical-alignment",
        "POLICY-jikuo-data-model-drift-alarm",
    ]
    for policy_id in policy_ids:
        shutil.copyfile(
            ROOT / ".jikuo" / "policies" / "approved" / f"{policy_id}.yaml",
            approved / f"{policy_id}.yaml",
        )
    manifest_lines = [
        'schema_version: "jikuo.policy_store_manifest.v0"',
        'project_id: "agent_flow_semantic_scope_distribution_fixture"',
        'store_root: ".jikuo/policies"',
        "active_policy_refs:",
    ]
    for policy_id in policy_ids:
        manifest_lines.extend(
            [
                f'  - policy_id: "{policy_id}"',
                "    version: 1",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
            ]
        )
    manifest_lines.extend(
        [
            "proposal_refs: []",
            "deprecated_policy_refs: []",
            "superseded_policy_refs: []",
            'last_updated_at: "2026-05-30T00:00:00Z"',
            "compatibility:",
            '  unknown_fields: "preserve"',
            '  writer: "test_fixture"',
            "",
        ]
    )
    (store / "manifest.yaml").write_text("\n".join(manifest_lines), encoding="utf-8")


def write_progress_summary_policy_store(root: Path) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    policy_id = "POLICY-jikuo-progress-summary-business-meaning"
    shutil.copyfile(
        ROOT / ".jikuo" / "policies" / "approved" / f"{policy_id}.yaml",
        approved / f"{policy_id}.yaml",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "agent_flow_progress_summary_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{policy_id}"',
                "    version: 1",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
                "proposal_refs: []",
                "deprecated_policy_refs: []",
                "superseded_policy_refs: []",
                'last_updated_at: "2026-06-03T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_main_doc_mount_policy_store(root: Path) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    policy_id = "POLICY-jikuo-main-doc-mount-maintenance"
    (approved / f"{policy_id}.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                f'policy_id: "{policy_id}"',
                "version: 1",
                'status: "active_report_only"',
                'title: "Main development document mount maintenance before slice completion"',
                'scenario_package: "self_bootstrap_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                '    ref: "tests:main_doc_mount_policy"',
                "triggers:",
                '  - trigger_id: "TRG-completion-review"',
                '    type: "task_lifecycle_event"',
                '    event: "completion_review"',
                "conditions:",
                "  []",
                "required_actions:",
                '  - action_id: "ACT-main-doc-mount-maintenance"',
                '    type: "maintain_main_document_mounts_and_update_scope_before_completion"',
                "required_evidence:",
                '  - evidence_id: "EVD-main-doc-mount-maintenance"',
                '    type: "main_document_mount_maintenance_evidence"',
                '    satisfies_action: "ACT-main-doc-mount-maintenance"',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "agent_flow_main_doc_mount_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{policy_id}"',
                "    version: 1",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
                "proposal_refs:",
                "  []",
                "deprecated_policy_refs:",
                "  []",
                "superseded_policy_refs:",
                "  []",
                'last_updated_at: "2026-05-14T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_task_session_binding_policy_store(root: Path) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    policy_id = "POLICY-jikuo-task-session-binding-at-slice-start"
    (approved / f"{policy_id}.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                f'policy_id: "{policy_id}"',
                "version: 2",
                'status: "active_report_only"',
                'title: "Task-session binding at governed slice start"',
                'scenario_package: "self_bootstrap_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                '    ref: "tests:task_session_binding_policy"',
                "triggers:",
                '  - trigger_id: "TRG-task-start"',
                '    type: "task_lifecycle_event"',
                '    event: "task_start"',
                "conditions: []",
                "required_actions:",
                '  - action_id: "ACT-bind-create-or-explicitly-defer-task-session"',
                '    type: "bind_create_or_explicitly_defer_task_session"',
                "required_evidence:",
                '  - evidence_id: "EVD-task-session-binding-evidence"',
                '    type: "task_session_binding_evidence"',
                '    satisfies_action: "ACT-bind-create-or-explicitly-defer-task-session"',
                '    required_status: ["ok", "needs_user_decision", "explicitly_deferred"]',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "agent_flow_task_session_binding_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{policy_id}"',
                "    version: 2",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
                "proposal_refs:",
                "  []",
                "deprecated_policy_refs:",
                "  []",
                "superseded_policy_refs:",
                "  []",
                'last_updated_at: "2026-05-14T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


class AgentFlowProposalTests(unittest.TestCase):
    def test_task_start_propose_json_composes_no_write_atoms(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Agent Flow Probe",
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["schema"], "jikuo.agent_flow_proposal.v1")
        self.assertEqual(
            proposal["chat_ready_markdown_schema"],
            "jikuo.chat_ready_markdown.v0",
        )
        self.assertIn("# JIKUO Agent Flow Proposal", proposal["chat_ready_markdown"])
        self.assertIn("## Cards", proposal["chat_ready_markdown"])
        self.assertEqual(proposal["previous_schema"], "jikuo.agent_flow_proposal.v0")
        self.assertTrue(proposal["report_only"])
        self.assertEqual(proposal["runner_mode"], "propose")
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertIn(
            "does not create .jikuo/policies/",
            proposal["write_effect"]["non_effects"],
        )
        self.assertEqual(proposal["trigger_decision"]["invocation_scenario"], "task_start")
        self.assertEqual(proposal["trigger_decision"]["confidence"], "event_match")
        self.assertEqual(
            proposal["trigger_decision"]["confidence_basis"],
            "canonical_event_mapping",
        )
        self.assertEqual(
            proposal["trigger_decision"]["intent_classification"]["confidence"],
            "not_evaluated_by_runner",
        )
        self.assertEqual(proposal["trigger_decision"]["execution_readiness"], "ready")
        self.assertEqual(proposal["work_profile"]["schema"], "jikuo.work_profile.v0")
        self.assertEqual(proposal["work_profile"]["lifecycle_event"], "task_start")
        self.assertIn("discussion", proposal["work_profile"]["policy_scopes"])
        self.assertIn("editing", proposal["work_profile"]["policy_scopes"])
        self.assertTrue(proposal["work_profile"]["fallback_expanded"])
        self.assertIn("## Work Profile", proposal["chat_ready_markdown"])
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "missing")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "not_evaluated")
        self.assertEqual(proposal["triggered_policies"], [])
        self.assertEqual(proposal["required_actions"], [])
        self.assertEqual(proposal["evidence_status"], [])
        self.assertEqual(proposal["missing_evidence_reports"], [])
        self.assertEqual(proposal["policy_feedback_options"], [])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-TASK-START-PROCESSING-01", atom_ids)
        self.assertIn("CAP-TASK-START-DRYRUN-01", atom_ids)
        self.assertIn("CAP-CARD-TASKSESSION-01", atom_ids)
        self.assertIn("CAP-POLICY-STORE-STATUS-01", atom_ids)
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_start_processing")
        self.assertEqual(
            proposal["cards"][0]["task_start_resolution"]["status"],
            "processing_started",
        )
        self.assertEqual(proposal["cards"][1]["card_kind"], "task_session_start_preview")
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_conversation_turn_router_noop_is_no_write_and_auditable(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "semantic",
                "--user-phrase",
                "thanks for the update",
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["work_profile"]["schema"], "jikuo.work_profile.v0")
        self.assertEqual(
            proposal["work_profile"]["lifecycle_event"],
            "conversation_turn",
        )
        self.assertEqual(proposal["work_profile"]["intent_class"], "discussion")
        self.assertEqual(proposal["work_profile"]["operation_class"], "no_tool")
        self.assertEqual(proposal["work_profile"]["policy_scopes"], ["discussion"])
        self.assertFalse(proposal["work_profile"]["fallback_expanded"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "conversation_turn",
        )
        self.assertEqual(
            proposal["trigger_decision"]["trigger_source"],
            "conversation_turn_router",
        )
        self.assertEqual(
            proposal["trigger_decision"]["intent_classification"]["confidence"],
            "heuristic_router",
        )
        router = proposal["conversation_router"]
        self.assertEqual(router["schema"], "jikuo.conversation_turn_router.v0")
        self.assertEqual(router["trigger_mode"], "semantic")
        self.assertEqual(router["router_status"], "ok")
        self.assertEqual(router["required_followup_tools"], [])
        self.assertFalse(router["privacy"]["raw_transcript_captured"])
        self.assertEqual(
            router["classified_obligations"][0]["kind"],
            "no_jikuo_action_required",
        )
        cards = {card["card_kind"]: card for card in proposal["cards"]}
        self.assertIn("conversation_turn_router", cards)
        self.assertEqual(cards["conversation_turn_router"]["status"], "ok")
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-CONVERSATION-TURN-ROUTER-01", atom_ids)
        self.assertIn("Conversation-turn router", proposal["chat_ready_markdown"])
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_conversation_turn_mounted_idle_tick_is_auditable(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                "thanks for the update",
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
        proposal = json.loads(completed.stdout)
        router = proposal["conversation_router"]
        self.assertEqual(router["trigger_mode"], "mounted")
        self.assertEqual(router["router_status"], "ok")
        self.assertEqual(
            router["classified_obligations"][0]["kind"],
            "mounted_idle_tick",
        )
        self.assertIn("mounted_idle_tick", proposal["chat_ready_markdown"])
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_conversation_turn_router_reads_user_phrase_from_stdin(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase-stdin",
                "--project-root",
                str(READY_PROJECT),
                "--format",
                "json",
            ],
            cwd=ROOT,
            input="please show setup settings",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        proposal = json.loads(completed.stdout)
        self.assertEqual(
            proposal["trigger_decision"]["user_phrase"],
            "<redacted_user_phrase>",
        )
        self.assertEqual(
            proposal["trigger_decision"]["user_phrase_status"],
            "provided_redacted",
        )
        self.assertNotIn("please show setup settings", completed.stdout)
        router = proposal["conversation_router"]
        self.assertEqual(router["schema"], "jikuo.conversation_turn_router.v0")
        self.assertEqual(router["trigger_mode"], "mounted")
        self.assertEqual(
            router["required_followup_tools"],
            ["python -B -m jikuo.agent_flow propose --event configuration_review"],
        )
        self.assertFalse(proposal["write_effect"]["writes_performed"])

    def test_host_semantic_intent_guides_work_profile_before_keyword_fallback(self):
        semantic_intent = {
            "schema": "jikuo.host_semantic_intent.v0",
            "source_client": "codex",
            "source_event": "UserPromptSubmit",
            "provider": "host_ai",
            "confidence": "high",
            "constraints": ["no_file_write"],
            "requested_outcome": "compare the implementation approach without writing files",
            "process_contract": [
                "align concepts before implementation details",
                "critique the proposal against the business goal",
            ],
            "execution_boundary": "read_only",
            "response_contract": [
                "explain recommendation",
                "name residual risk",
            ],
            "intent_slices": [
                {
                    "id": "discuss_change",
                    "index": 1,
                    "user_expression": "discuss the implementation without writing files",
                    "policy_scopes": ["discussion"],
                    "intent_class": "design_discussion",
                    "operation_class": "no_change",
                    "output_class": "explanation",
                    "rationale_summary": "User asks to discuss the change without editing files.",
                }
            ],
            "work_profile": {
                "policy_scopes": ["discussion"],
                "intent_class": "design_discussion",
                "operation_class": "no_change",
                "output_class": "explanation",
            },
        }
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                "please modify the implementation but only discuss it; do not write files",
                "--host-semantic-intent-json",
                json.dumps(semantic_intent),
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
        self.assertNotIn(
            "please modify the implementation but only discuss it; do not write files",
            completed.stdout,
        )
        proposal = json.loads(completed.stdout)
        profile = proposal["work_profile"]
        self.assertEqual(profile["intent_class"], "design_discussion")
        self.assertEqual(profile["operation_class"], "no_change")
        self.assertEqual(profile["output_class"], "explanation")
        self.assertEqual(profile["policy_scopes"], ["discussion"])
        self.assertEqual(profile["confidence"], "high")
        contract = profile["policy_contract"]
        self.assertEqual(
            contract["requested_outcome"],
            "compare the implementation approach without writing files",
        )
        self.assertEqual(
            contract["process_contract"],
            [
                "align concepts before implementation details",
                "critique the proposal against the business goal",
            ],
        )
        self.assertEqual(contract["execution_boundary"], "read_only")
        self.assertEqual(
            contract["response_contract"],
            ["explain recommendation", "name residual risk"],
        )
        semantic = profile["basis"]["host_semantic_intent"]
        self.assertEqual(semantic["status"], "provided")
        self.assertEqual(semantic["provider"], "host_ai")
        self.assertEqual(semantic["constraints"], ["no_file_write"])
        self.assertEqual(semantic["policy_contract"], contract)
        self.assertEqual(len(semantic["intent_slices"]), 1)
        self.assertEqual(
            semantic["intent_slices"][0]["user_expression"],
            "discuss the implementation without writing files",
        )
        conflicts = profile["basis"]["conflicts"]
        self.assertEqual(
            conflicts[0]["signal"],
            "editing_terms_blocked_by_edit_constraint",
        )
        self.assertIn("Semantic intent status: `provided`", proposal["chat_ready_markdown"])
        semantic_evidence = proposal["semantic_intent_evidence"]
        self.assertFalse(semantic_evidence["required"])
        self.assertEqual(semantic_evidence["status"], "ok")
        self.assertEqual(semantic_evidence["provider"], "host_ai")
        self.assertIn("### Semantic Intent Evidence", proposal["chat_ready_markdown"])
        self.assertIn("- Status: `ok`", proposal["chat_ready_markdown"])
        self.assertIn(
            "user_expression=`discuss the implementation without writing files`",
            proposal["chat_ready_markdown"],
        )
        self.assertIn(
            "Requested outcome: `compare the implementation approach without writing files`",
            proposal["chat_ready_markdown"],
        )
        self.assertIn(
            "Process contract: `align concepts before implementation details; critique the proposal against the business goal`",
            proposal["chat_ready_markdown"],
        )
        self.assertIn("Execution boundary: `read_only`", proposal["chat_ready_markdown"])
        self.assertIn(
            "Response contract: `explain recommendation; name residual risk`",
            proposal["chat_ready_markdown"],
        )
        self.assertIn("Semantic/deterministic conflicts: `1`", proposal["chat_ready_markdown"])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-HOST-SEMANTIC-INTENT-WORK-PROFILE-01", atom_ids)

    def test_host_semantic_intent_projection_omits_raw_user_phrase(self):
        raw_prompt = "SECRET_SEMANTIC_SMOKE_VALUE: update hook docs and summarize why"
        semantic_intent = {
            "schema": "jikuo.host_semantic_intent.v0",
            "provider": "host_ai",
            "confidence": "high",
            "work_profile": {
                "policy_scopes": ["editing", "progress_summary"],
            },
            "intent_slices": [
                {
                    "id": "update_docs",
                    "user_expression": "update hook docs",
                    "policy_scopes": ["editing"],
                    "requested_outcome": "Update hook documentation.",
                },
                {
                    "id": "summarize_meaning",
                    "user_expression": "summarize why",
                    "policy_scopes": ["progress_summary"],
                    "response_contract": ["include technical and business meaning"],
                },
            ],
        }
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                raw_prompt,
                "--host-semantic-intent-json",
                json.dumps(semantic_intent),
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
        self.assertNotIn(raw_prompt, completed.stdout)
        proposal = json.loads(completed.stdout)
        semantic = proposal["work_profile"]["basis"]["host_semantic_intent"]
        self.assertEqual(semantic["status"], "provided")
        self.assertEqual(
            proposal["work_profile"]["policy_scopes"],
            ["editing", "progress_summary", "discussion"],
        )
        self.assertEqual(len(semantic["intent_slices"]), 2)
        self.assertIn("user_expression=`update hook docs`", proposal["chat_ready_markdown"])

    def test_host_semantic_intent_preserves_multi_intent_aggregate_scopes(self):
        semantic_intent = {
            "schema": "jikuo.host_semantic_intent.v0",
            "source_client": "codex",
            "source_event": "UserPromptSubmit",
            "provider": "host_ai",
            "confidence": "medium",
            "multi_intent": True,
            "primary_intent_ref": "update_docs",
            "intent_slices": [
                {
                    "id": "explain_design",
                    "index": 1,
                    "user_expression": "review the design",
                    "policy_scopes": ["discussion", "first_principles_alignment"],
                    "intent_class": "design_explanation",
                    "operation_class": "read_only",
                    "output_class": "explanation",
                },
                {
                    "id": "update_docs",
                    "index": 2,
                    "user_expression": "update the docs",
                    "policy_scopes": ["editing"],
                    "intent_class": "implementation_request",
                    "operation_class": "documentation_update",
                    "output_class": "repository_change",
                },
                {
                    "id": "summarize_progress",
                    "index": 3,
                    "user_expression": (
                        "summarize progress and business meaning with a very long "
                        "expression that should be shortened before it is rendered "
                        "into the runtime card because it must not become raw prompt storage"
                    ),
                    "policy_scopes": ["progress_summary"],
                    "intent_class": "progress_summary",
                    "operation_class": "summarize",
                    "output_class": "summary",
                },
            ],
        }
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                "please handle this turn",
                "--host-semantic-intent-json",
                json.dumps(semantic_intent),
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
        proposal = json.loads(completed.stdout)
        profile = proposal["work_profile"]
        self.assertEqual(
            profile["policy_scopes"],
            ["discussion", "editing", "progress_summary"],
        )
        semantic = profile["basis"]["host_semantic_intent"]
        self.assertTrue(semantic["multi_intent"])
        self.assertEqual(semantic["primary_intent_ref"], "update_docs")
        self.assertEqual(len(semantic["intent_slices"]), 3)
        self.assertEqual(semantic["intent_slices"][0]["policy_scopes"], ["discussion"])
        self.assertNotIn(
            "first_principles_alignment",
            json.dumps(semantic, ensure_ascii=False),
        )
        self.assertEqual(semantic["intent_slices"][1]["index"], 2)
        self.assertLessEqual(len(semantic["intent_slices"][2]["user_expression"]), 120)
        self.assertIn("Intent slices: `3`", proposal["chat_ready_markdown"])
        self.assertIn("`1`: id=`explain_design`; scopes=`discussion`", proposal["chat_ready_markdown"])
        self.assertIn("`2`: id=`update_docs`; scopes=`editing`", proposal["chat_ready_markdown"])
        self.assertIn("user_expression=`update the docs`", proposal["chat_ready_markdown"])

    def test_host_semantic_intent_scopes_change_policy_distribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_semantic_scope_distribution_policy_store(project_root)

            def propose_with_scope(scope: str) -> dict:
                semantic_intent = {
                    "schema": "jikuo.host_semantic_intent.v0",
                    "provider": "host_ai",
                    "confidence": "high",
                    "work_profile": {
                        "intent_class": (
                            "design_discussion"
                            if scope == "discussion"
                            else "implementation_request"
                        ),
                        "operation_class": "no_change" if scope == "discussion" else "write_file",
                        "output_class": "explanation" if scope == "discussion" else "repository_change",
                        "policy_scopes": [scope],
                    },
                    "intent_slices": [
                        {
                            "id": f"{scope}_slice",
                            "index": 1,
                            "user_expression": "handle item alpha",
                            "policy_scopes": [scope],
                            "requested_outcome": "route policy from host semantic scope",
                            "response_contract": ["show which policy matched"],
                        }
                    ],
                }
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(TOOL),
                        "propose",
                        "--event",
                        "conversation_turn",
                        "--trigger-mode",
                        "mounted",
                        "--user-phrase",
                        "please handle item alpha",
                        "--host-semantic-intent-json",
                        json.dumps(semantic_intent),
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
                return json.loads(completed.stdout)

            discussion = propose_with_scope("discussion")
            editing = propose_with_scope("editing")

            self.assertEqual(discussion["work_profile"]["policy_scopes"], ["discussion"])
            self.assertEqual(editing["work_profile"]["policy_scopes"], ["editing"])
            self.assertEqual(
                [policy["policy_ref"] for policy in discussion["triggered_policies"]],
                ["POLICY-jikuo-first-principles-critical-alignment"],
            )
            self.assertEqual(
                [policy["policy_ref"] for policy in editing["triggered_policies"]],
                ["POLICY-jikuo-data-model-drift-alarm"],
            )
            self.assertIn(
                "policy_scope:discussion",
                discussion["triggered_policies"][0]["work_profile_match"]["matched_refs"],
            )
            self.assertIn(
                "policy_scope:editing",
                editing["triggered_policies"][0]["work_profile_match"]["matched_refs"],
            )
            self.assertIn("Semantic intent status: `provided`", discussion["chat_ready_markdown"])
            self.assertIn("Semantic intent status: `provided`", editing["chat_ready_markdown"])

    def test_scope_only_policy_distribution_is_not_blocked_by_task_start_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            create_agent_flow_ready_project(project_root)
            write_semantic_scope_distribution_policy_store(project_root)
            semantic_intent = {
                "schema": "jikuo.host_semantic_intent.v0",
                "provider": "host_ai",
                "confidence": "high",
                "work_profile": {
                    "intent_class": "implementation_request",
                    "operation_class": "write_file",
                    "output_class": "repository_change",
                    "policy_scopes": ["editing"],
                },
                "requested_outcome": "route editing policy from task start surface",
                "execution_boundary": "no durable write in test",
                "response_contract": ["show which policy matched"],
            }
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Apply scoped implementation update",
                    "--host-semantic-intent-json",
                    json.dumps(semantic_intent),
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
            proposal = json.loads(completed.stdout)
            self.assertEqual(proposal["work_profile"]["policy_scopes"], ["editing"])
            self.assertEqual(
                [policy["policy_ref"] for policy in proposal["triggered_policies"]],
                ["POLICY-jikuo-data-model-drift-alarm"],
            )
            triggered = proposal["triggered_policies"][0]
            self.assertEqual(triggered["trigger_match_mode"], "work_profile_scope")
            self.assertEqual(triggered["declared_trigger_event"], "conversation_turn")
            self.assertEqual(triggered["evaluation_event"], "task_start")
            self.assertIn("work_profile scope matched", triggered["trigger_reason"])
            self.assertIn(
                "work_profile scope matched during task_start",
                proposal["chat_ready_markdown"],
            )

    def test_progress_summary_policy_triggers_from_conversation_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            create_agent_flow_ready_project(project_root)
            write_progress_summary_policy_store(project_root)
            semantic_intent = {
                "schema": "jikuo.host_semantic_intent.v0",
                "provider": "host_ai",
                "confidence": "high",
                "policy_scopes": ["progress_summary"],
                "requested_outcome": "summarize progress and remaining todos",
                "execution_boundary": "no file writes required for this summary",
                "response_contract": [
                    "include product or business meaning for major items",
                    "separate completed work from next todos",
                ],
                "intent_slices": [
                    {
                        "id": "progress_summary",
                        "index": 1,
                        "user_expression": "总结进度，输出代办",
                        "policy_scopes": ["progress_summary"],
                        "requested_outcome": "summarize current progress and next todos",
                    }
                ],
            }
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "conversation_turn",
                    "--trigger-mode",
                    "mounted",
                    "--user-phrase",
                    "\u603b\u7ed3\u8fdb\u5ea6\uff0c\u8f93\u51fa\u4ee3\u529e",
                    "--host-semantic-intent-json",
                    json.dumps(semantic_intent),
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
            proposal = json.loads(completed.stdout)
            self.assertEqual(proposal["work_profile"]["policy_scopes"], ["progress_summary"])
            self.assertEqual(proposal["semantic_intent_evidence"]["status"], "ok")
            self.assertEqual(
                [policy["policy_ref"] for policy in proposal["triggered_policies"]],
                ["POLICY-jikuo-progress-summary-business-meaning"],
            )
            triggered = proposal["triggered_policies"][0]
            self.assertEqual(triggered["trigger_match_mode"], "work_profile_scope")
            self.assertEqual(triggered["declared_trigger_event"], "completion_review")
            self.assertEqual(triggered["evaluation_event"], "conversation_turn")
            self.assertIn(
                "policy_scope:progress_summary",
                triggered["work_profile_match"]["matched_refs"],
            )
            self.assertIn(
                "work_profile scope matched during conversation_turn",
                proposal["chat_ready_markdown"],
            )

    def test_work_profile_does_not_treat_no_write_as_editing(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "semantic",
                "--user-phrase",
                "this is a no-write review",
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["work_profile"]["schema"], "jikuo.work_profile.v0")
        self.assertEqual(
            proposal["work_profile"]["lifecycle_event"],
            "conversation_turn",
        )
        self.assertEqual(proposal["work_profile"]["intent_class"], "discussion")
        self.assertEqual(proposal["work_profile"]["operation_class"], "no_tool")
        self.assertEqual(proposal["work_profile"]["policy_scopes"], ["discussion"])
        self.assertFalse(proposal["semantic_intent_evidence"]["required"])
        self.assertEqual(proposal["semantic_intent_evidence"]["status"], "not_required")
        self.assertIn("### Semantic Intent Evidence", proposal["chat_ready_markdown"])
        self.assertIn("- Required: `false`", proposal["chat_ready_markdown"])

    def test_semantic_intent_evidence_missing_for_editing_without_host_intent(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                "please update docs and summarize progress",
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
        proposal = json.loads(completed.stdout)
        evidence = proposal["semantic_intent_evidence"]
        self.assertTrue(evidence["required"])
        self.assertEqual(evidence["status"], "missing")
        self.assertEqual(evidence["provider"], "unavailable")
        self.assertEqual(
            evidence["followup"],
            "provide_host_semantic_intent_and_rerun_route",
        )
        self.assertIn("editing_intent", evidence["reasons"])
        self.assertIn("progress_summary_intent", evidence["reasons"])
        self.assertEqual(
            proposal["work_profile"]["semantic_intent_evidence"],
            evidence,
        )
        self.assertIn(
            "provide compact host_semantic_intent",
            proposal["next_actions"][0],
        )
        self.assertIn("### Semantic Intent Evidence", proposal["chat_ready_markdown"])
        self.assertIn("- Required: `true`", proposal["chat_ready_markdown"])
        self.assertIn("- Status: `missing`", proposal["chat_ready_markdown"])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-SEMANTIC-INTENT-CLASSIFICATION-EVIDENCE-01", atom_ids)

    def test_bilingual_keyword_fallback_detects_chinese_editing_and_progress(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                (
                    "\u8bf7\u66f4\u65b0\u6587\u6863\uff0c"
                    "\u56de\u586b\u6ce8\u518c\u4fe1\u606f\uff0c"
                    "\u7136\u540e\u603b\u7ed3\u8fdb\u5ea6\u548c\u5269\u4f59\u4ee3\u529e"
                ),
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
        proposal = json.loads(completed.stdout)
        profile = proposal["work_profile"]
        self.assertEqual(profile["intent_class"], "editing")
        self.assertIn("editing", profile["policy_scopes"])
        self.assertIn("progress_summary", profile["policy_scopes"])
        signals = {
            item["signal"]
            for item in profile["basis"]["deterministic_signals"]
        }
        self.assertIn("editing_terms", signals)
        self.assertIn("progress_summary_terms", signals)

    def test_bilingual_keyword_fallback_respects_chinese_no_edit_constraint(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                "\u53ea\u8ba8\u8bba\u600e\u4e48\u4fee\u6539\uff0c\u4e0d\u8981\u52a8\u6587\u4ef6",
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
        proposal = json.loads(completed.stdout)
        profile = proposal["work_profile"]
        self.assertEqual(profile["policy_scopes"], ["discussion"])
        self.assertNotIn("editing", profile["policy_scopes"])
        self.assertEqual(
            profile["basis"]["conflicts"][0]["signal"],
            "editing_terms_blocked_by_edit_constraint",
        )
        signals = {
            item["signal"]
            for item in profile["basis"]["deterministic_signals"]
        }
        self.assertIn("deterministic_edit_blocking_terms", signals)

    def test_bilingual_keyword_fallback_detects_expanded_english_editing_terms(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                "please refactor the hook docs and add tests",
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
        proposal = json.loads(completed.stdout)
        profile = proposal["work_profile"]
        self.assertEqual(profile["intent_class"], "editing")
        self.assertIn("editing", profile["policy_scopes"])
        signals = {
            item["signal"]
            for item in profile["basis"]["deterministic_signals"]
        }
        self.assertIn("editing_terms", signals)

    def test_conversation_turn_router_detects_policy_and_task_obligations(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
                "--trigger-mode",
                "mounted",
                "--user-phrase",
                "以后列出进度和代办时请说明业务意义，并继续实现 router",
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["status"], "review")
        router = proposal["conversation_router"]
        self.assertEqual(router["trigger_mode"], "mounted")
        self.assertEqual(router["router_status"], "requires_action")
        obligation_kinds = {
            obligation["kind"]
            for obligation in router["classified_obligations"]
        }
        self.assertIn("task_start", obligation_kinds)
        self.assertIn("policy_suggestion_review", obligation_kinds)
        self.assertIn(
            "jikuo.propose_task_start",
            router["required_followup_tools"],
        )
        cards = {card["card_kind"]: card for card in proposal["cards"]}
        self.assertIn("policy_suggestion_review", cards)
        self.assertEqual(cards["policy_suggestion_review"]["status"], "review")
        self.assertEqual(
            cards["policy_suggestion_review"]["policy_suggestion_review"][
                "candidate_count"
            ],
            1,
        )
        self.assertIn("policy_suggestion_review", proposal["chat_ready_markdown"])
        self.assertIn("trigger_mode: mounted", proposal["chat_ready_markdown"])
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_conversation_turn_router_requires_user_phrase(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "conversation_turn",
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

        self.assertEqual(completed.returncode, 2, completed.stderr)
        proposal = json.loads(completed.stdout)
        router = proposal["conversation_router"]
        self.assertEqual(router["router_status"], "clarification_required")
        self.assertIn(
            "user_phrase_required_for_conversation_turn_router",
            proposal["trigger_decision"]["required_clarification"],
        )
        cards = {card["card_kind"]: card for card in proposal["cards"]}
        self.assertEqual(cards["conversation_turn_router"]["status"], "refused")
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_conversation_turn_policy_suggestion_review_satisfies_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_conversation_policy_suggestion_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "conversation_turn",
                    "--trigger-mode",
                    "mounted",
                    "--user-phrase",
                    (
                        "I keep asking for progress, todo, and business meaning "
                        "because this repeated need should become reviewable."
                    ),
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
            proposal = json.loads(completed.stdout)
            obligation_kinds = {
                obligation["kind"]
                for obligation in proposal["conversation_router"][
                    "classified_obligations"
                ]
            }
            self.assertIn("policy_suggestion_review", obligation_kinds)
            self.assertNotIn("completion_review", obligation_kinds)
            cards = {card["card_kind"]: card for card in proposal["cards"]}
            self.assertIn("policy_suggestion_review", cards)
            review = cards["policy_suggestion_review"]["policy_suggestion_review"]
            self.assertEqual(review["schema"], "jikuo.proactive_policy_suggestion_review.v0")
            self.assertEqual(review["review_status"], "candidate_detected")
            self.assertEqual(review["candidate_count"], 1)
            self.assertFalse(review["privacy"]["raw_transcript_captured"])
            atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
            self.assertIn("CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01", atom_ids)
            self.assertEqual(len(proposal["triggered_policies"]), 1)
            self.assertEqual(proposal["missing_evidence_reports"], [])
            evidence = proposal["evidence_status"][0]
            self.assertEqual(evidence["current_status"], "ok")
            self.assertEqual(
                evidence["required_type"],
                "proactive_policy_suggestion_review_evidence",
            )
            self.assertIn(
                "proactive_policy_suggestion_review_evidence",
                proposal["chat_ready_markdown"],
            )
            self.assertFalse(proposal["write_effect"]["writes_performed"])
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_conversation_turn_policy_suggestion_handles_editing_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_conversation_policy_suggestion_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "conversation_turn",
                    "--trigger-mode",
                    "mounted",
                    "--user-phrase",
                    "Please commit the changes and remember that I often ask for this.",
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
            proposal = json.loads(completed.stdout)
            self.assertEqual(proposal["work_profile"]["lifecycle_event"], "conversation_turn")
            self.assertIn("editing", proposal["work_profile"]["policy_scopes"])
            self.assertEqual(len(proposal["triggered_policies"]), 1)
            triggered = proposal["triggered_policies"][0]
            self.assertEqual(
                triggered["policy_ref"],
                "POLICY-jikuo-conversation-level-proactive-policy-suggestion",
            )
            self.assertEqual(triggered["work_profile_match"]["status"], "matched")
            self.assertIn(
                "policy_scope:editing",
                triggered["work_profile_match"]["matched_refs"],
            )
            self.assertFalse(proposal["missing_evidence_reports"])

    def test_conversation_turn_policy_suggestion_review_records_no_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_conversation_policy_suggestion_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "conversation_turn",
                    "--user-phrase",
                    "thanks for the update",
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
            proposal = json.loads(completed.stdout)
            cards = {card["card_kind"]: card for card in proposal["cards"]}
            review = cards["policy_suggestion_review"]["policy_suggestion_review"]
            self.assertEqual(review["review_status"], "reviewed_no_candidate")
            self.assertEqual(review["candidate_count"], 0)
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
            self.assertFalse(proposal["write_effect"]["writes_performed"])
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_missing_project_status_markdown_remains_no_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "status",
                "--project-root",
                str(MISSING_PROJECT),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("JIKUO Agent Flow Proposal", completed.stdout)
        self.assertIn("Writes performed: `false`", completed.stdout)
        self.assertIn("Match confidence: `event_match`", completed.stdout)
        self.assertIn("Match basis: `canonical_event_mapping`", completed.stdout)
        self.assertIn("Intent confidence: `not_evaluated_by_runner`", completed.stdout)
        self.assertNotIn("Confidence: `high`", completed.stdout)
        self.assertIn("Policy Context", completed.stdout)
        self.assertIn("Policy store status: `missing`", completed.stdout)
        self.assertIn("Policy eval status: `not_evaluated`", completed.stdout)
        self.assertIn("CAP-PROJECT-STATE-STATUS-01", completed.stdout)
        self.assertIn("CAP-PROJECT-STATE-INIT-DRYRUN-01", completed.stdout)
        self.assertFalse((MISSING_PROJECT / ".jikuo").exists())

    def test_task_continue_without_session_id_refuses_without_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_continue",
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

        self.assertEqual(completed.returncode, 2, completed.stderr)
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["status"], "refused")
        self.assertEqual(proposal["trigger_decision"]["confidence"], "event_match")
        self.assertEqual(proposal["trigger_decision"]["execution_readiness"], "blocked")
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_continue_refusal")
        self.assertIn(
            "session_id_required_for_task_continue",
            proposal["cards"][0]["refusal_reasons"],
        )
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "missing")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "not_evaluated")
        self.assertEqual(proposal["missing_evidence_reports"], [])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_active_policy_store_triggers_exact_lifecycle_policy(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Policy Store Probe",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "evaluated")
        self.assertEqual(
            proposal["policy_context"]["policy_evidence_check_status"],
            "checked",
        )
        self.assertEqual(len(proposal["policy_context"]["active_policy_refs"]), 1)
        self.assertEqual(
            proposal["policy_context"]["active_policy_refs"][0]["policy_id"],
            "POLICY-three-phase-audit",
        )
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-three-phase-audit",
        )
        self.assertEqual(proposal["triggered_policies"][0]["confidence"], "tool_verified")
        self.assertEqual(len(proposal["required_actions"]), 1)
        self.assertEqual(
            proposal["required_actions"][0]["action_type"],
            "render_pre_task_review",
        )
        self.assertEqual(len(proposal["evidence_status"]), 1)
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            proposal["evidence_status"][0]["required_type"],
            "card_rendered",
        )
        self.assertEqual(proposal["missing_evidence_reports"], [])
        runtime_cards = [
            card
            for card in proposal["cards"]
            if card["card_kind"] == "policy_runtime_status"
        ]
        self.assertEqual(len(runtime_cards), 1)
        runtime_status = runtime_cards[0]["policy_runtime_status"]
        self.assertEqual(
            runtime_status["schema"],
            "jikuo.policy_runtime_status.v0",
        )
        self.assertEqual(runtime_status["active_policy_count"], 1)
        self.assertEqual(runtime_status["triggered_policy_count"], 1)
        self.assertEqual(runtime_status["not_triggered_policy_count"], 0)
        self.assertEqual(runtime_status["missing_evidence_count"], 0)
        self.assertEqual(
            runtime_status["triggered_policies"][0]["policy_ref"],
            "POLICY-three-phase-audit",
        )
        self.assertIn("## Policy runtime status", proposal["chat_ready_markdown"])
        self.assertIn("POLICY-three-phase-audit", proposal["chat_ready_markdown"])
        self.assertEqual(
            proposal["display"]["schema"],
            "jikuo.display_directives.v0",
        )
        self.assertEqual(
            proposal["display"]["card_priority_order"][0],
            "policy_runtime_status",
        )
        cards_index = proposal["chat_ready_markdown"].index("## Cards")
        policy_card_index = proposal["chat_ready_markdown"].index(
            "## Policy runtime status",
            cards_index,
        )
        task_card_index = proposal["chat_ready_markdown"].index(
            "## Task-session start preview",
            cards_index,
        )
        trigger_index = proposal["chat_ready_markdown"].index("## Trigger Decision")
        self.assertLess(policy_card_index, task_card_index)
        self.assertLess(policy_card_index, trigger_index)
        self.assertEqual(
            {item["feedback_type"] for item in proposal["policy_feedback_options"]},
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertEqual(
            {
                item["persistence"]
                for item in proposal["policy_feedback_options"]
            },
            {"not_persisted_by_agent_flow_propose"},
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-STORE-STATUS-01", atom_ids)
        self.assertIn("CAP-POLICY-TRIGGER-EVALUATE-01", atom_ids)
        self.assertIn("CAP-POLICY-EVIDENCE-CHECK-01", atom_ids)
        self.assertFalse((POLICY_ACTIVE_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_work_profile_applicability_blocks_mismatched_runtime_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)
            add_policy_work_profile_applicability(
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-three-phase-audit.yaml"
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
                    "Work Profile Applicability Probe",
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
            proposal = json.loads(completed.stdout)
            self.assertEqual(len(proposal["triggered_policies"]), 0)
            runtime_cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_runtime_status"
            ]
            self.assertEqual(len(runtime_cards), 1)
            dead_zone = runtime_cards[0]["policy_runtime_status"]["policy_dead_zone"]
            self.assertEqual(dead_zone["classification"], "work_profile_scope_mismatch")
            self.assertIn(
                "not_triggered_policy: POLICY-three-phase-audit",
                "\n".join(runtime_cards[0]["shown_outputs"]),
            )
            self.assertIn(
                "work_profile lifecycle_event task_start did not match",
                proposal["chat_ready_markdown"],
            )
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_work_profile_applicability_surfaces_scope_match_runtime_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)
            add_matching_policy_work_profile_applicability(
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-three-phase-audit.yaml"
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
                    "Work Profile Applicability Probe",
                    "--project-root",
                    str(project_root),
                    "--changed-path",
                    "src/jikuo/agent_flow.py",
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
            self.assertEqual(len(proposal["triggered_policies"]), 1)
            triggered = proposal["triggered_policies"][0]
            self.assertEqual(triggered["policy_ref"], "POLICY-three-phase-audit")
            self.assertEqual(
                triggered["applies_to_work_profile"]["evaluator_effect"],
                "consumed_by_POLTRIG_03_scope_filter",
            )
            self.assertEqual(triggered["work_profile_match"]["status"], "matched")
            runtime_cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_runtime_status"
            ]
            self.assertEqual(len(runtime_cards), 1)
            shown_outputs = "\n".join(runtime_cards[0]["shown_outputs"])
            self.assertIn(
                "triggered_policy_work_profile_applicability: POLICY-three-phase-audit",
                shown_outputs,
            )
            self.assertIn(
                "triggered_policy_work_profile_match: POLICY-three-phase-audit",
                shown_outputs,
            )
            self.assertIn(
                "evaluator_effect=consumed_by_POLTRIG_03_scope_filter",
                proposal["chat_ready_markdown"],
            )
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_policy_evidence_record_proposes_guarded_append_without_write(self):
        session_file = (
            POLICY_EVIDENCE_SESSION_PROJECT
            / ".jikuo"
            / "task_sessions"
            / "task_policy_evidence_probe.yaml"
        )
        before_text = session_file.read_text(encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evidence_record",
                "--session-id",
                "task_policy_evidence_probe",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--action-ref",
                "ACT-render-pre-task-review",
                "--requirement-ref",
                "EVD-card-rendered",
                "--evidence-kind",
                "card_rendered",
                "--evidence-ref",
                "EVD-card-rendered",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(proposal["trigger_decision"]["invocation_scenario"], "policy_evidence_record")
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01", atom_ids)
        self.assertIn("CAP-TASK-UPDATE-DRYRUN-01", atom_ids)
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_session_evidence_append")
        command = proposal["cards"][0]["command_proposal"]["command_preview"]
        self.assertIn("python -B -m jikuo.task_session", command)
        self.assertNotIn("tools/jikuo", command)
        self.assertIn("--append-evidence", command)
        self.assertIn("--confirm-update-task-session", command)
        self.assertIn("--approval-phrase", command)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_policy_feedback_record_proposes_guarded_append_without_write(self):
        session_file = (
            POLICY_EVIDENCE_SESSION_PROJECT
            / ".jikuo"
            / "task_sessions"
            / "task_policy_evidence_probe.yaml"
        )
        before_text = session_file.read_text(encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_feedback_record",
                "--session-id",
                "task_policy_evidence_probe",
                "--policy-ref",
                "POLICY-real-test-data-and-chain",
                "--feedback-type",
                "not_applicable",
                "--summary",
                "User marked this triggered policy as not applicable for this task.",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_feedback_record",
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-FEEDBACK-PERSIST-PROPOSE-01", atom_ids)
        self.assertIn("CAP-TASK-UPDATE-DRYRUN-01", atom_ids)
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_session_evidence_append")
        command = proposal["cards"][0]["command_proposal"]["command_preview"]
        self.assertIn("python -B -m jikuo.task_session", command)
        self.assertNotIn("tools/jikuo", command)
        self.assertIn("--append-evidence", command)
        self.assertIn("policy_feedback:not_applicable", command)
        self.assertIn("policy_ref=POLICY-real-test-data-and-chain", command)
        self.assertIn("feedback_type=not_applicable", command)
        self.assertIn("--confirm-update-task-session", command)
        self.assertIn("--approval-phrase", command)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_policy_feedback_record_refuses_without_summary_or_user_phrase(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_feedback_record",
                "--session-id",
                "task_policy_evidence_probe",
                "--policy-ref",
                "POLICY-real-test-data-and-chain",
                "--feedback-type",
                "defer",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["status"], "refused")
        self.assertEqual(proposal["cards"][0]["card_kind"], "policy_feedback_record_refusal")
        self.assertIn(
            "summary_or_user_phrase_required_for_policy_feedback_record",
            proposal["cards"][0]["refusal_reasons"],
        )
        self.assertFalse(
            (POLICY_EVIDENCE_SESSION_PROJECT / ".jikuo" / "policies").exists()
        )

    def test_apply_task_session_evidence_update_refuses_without_approval(self):
        session_file = (
            POLICY_EVIDENCE_SESSION_PROJECT
            / ".jikuo"
            / "task_sessions"
            / "task_policy_evidence_probe.yaml"
        )
        before_text = session_file.read_text(encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "apply",
                "--operation",
                "task_session_evidence_update",
                "--session-id",
                "task_policy_evidence_probe",
                "--evidence-kind",
                "policy_feedback:not_applicable",
                "--evidence-ref",
                "policy_ref=POLICY-real-test-data-and-chain;feedback_type=not_applicable",
                "--summary",
                "User marked this triggered policy as not applicable for this task.",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        report = json.loads(completed.stdout)
        self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
        self.assertEqual(
            report["chat_ready_markdown_schema"],
            "jikuo.chat_ready_markdown.v0",
        )
        self.assertIn("# JIKUO Agent Flow Apply Result", report["chat_ready_markdown"])
        self.assertFalse(report["write_performed"])
        self.assertEqual(report["status"], "refused")
        self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
        self.assertIn("approval_evidence_missing", report["refusal_reasons"])
        atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
        self.assertIn("CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01", atom_ids)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_apply_task_session_evidence_update_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_evidence_session_project"
            shutil.copytree(POLICY_EVIDENCE_SESSION_PROJECT, project_copy)
            session_file = (
                project_copy
                / ".jikuo"
                / "task_sessions"
                / "task_policy_evidence_probe.yaml"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "task_session_evidence_update",
                    "--session-id",
                    "task_policy_evidence_probe",
                    "--evidence-kind",
                    "policy_feedback:not_applicable",
                    "--evidence-ref",
                    "policy_ref=POLICY-real-test-data-and-chain;feedback_type=not_applicable",
                    "--summary",
                    "User marked this triggered policy as not applicable for this task.",
                    "--project-root",
                    str(project_copy),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve this task-session evidence append.",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.task_session_update_result.v0",
            )
            self.assertTrue(
                report["target_result"]["verification"]["patch_applied"]
            )
            updated = session_file.read_text(encoding="utf-8")
            self.assertIn("policy_feedback:not_applicable", updated)
            self.assertIn("POLICY-real-test-data-and-chain", updated)
            self.assertIn(
                "User marked this triggered policy as not applicable for this task.",
                updated,
            )

    def test_apply_task_session_start_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "ready_project"
            project_copy.mkdir()
            create_agent_flow_ready_project(project_copy)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "task_session_start",
                    "--task-title",
                    "Agent Flow Start Apply Probe",
                    "--project-root",
                    str(project_copy),
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "task_session_start")
            self.assertEqual(report["status"], "refused")
            self.assertFalse(report["write_performed"])
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertFalse((project_copy / ".jikuo" / "task_sessions").exists())

    def test_apply_task_session_start_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "ready_project"
            project_copy.mkdir()
            create_agent_flow_ready_project(project_copy)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "task_session_start",
                    "--task-title",
                    "Agent Flow Start Apply Probe",
                    "--project-root",
                    str(project_copy),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve this task-session start through agent_flow.",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "task_session_start")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.task_session_write_result.v0",
            )
            target = Path(report["target_result"]["session_path"])
            self.assertTrue(target.is_file())
            self.assertTrue(
                report["target_result"]["verification"]["schema_ok"]
            )
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-TASK-START-WRITE-01", atom_ids)
            self.assertIn(
                "CAP-AGENT-FLOW-APPLY-TASK-SESSION-START-01",
                atom_ids,
            )

    def test_apply_starter_policy_pack_init_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "starter_project"
            project_root.mkdir()
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "starter_policy_pack_init",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "starter_policy_pack_init")
            self.assertEqual(report["status"], "refused")
            self.assertFalse(report["write_performed"])
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertFalse((project_root / ".jikuo").exists())

    def test_apply_starter_policy_pack_init_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "starter_project"
            project_root.mkdir()
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "starter_policy_pack_init",
                    "--project-root",
                    str(project_root),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve starter policy initialization through agent_flow.",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "starter_policy_pack_init")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.starter_policy_pack_init_result.v0",
            )
            self.assertTrue((project_root / ".jikuo" / "project_state.yaml").is_file())
            approved = project_root / ".jikuo" / "policies" / "approved"
            self.assertEqual(len(list(approved.glob("POLICY-*.yaml"))), 4)
            self.assertTrue(
                report["target_result"]["post_write_verification"]["starter_policies_active"]
            )
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-AGENT-FLOW-APPLY-STARTER-POLICY-PACK-01", atom_ids)

    def test_policy_distribution_review_resolves_natural_language_query_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "distribution_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "policy_distribution_review",
                    "--project-root",
                    str(project_root),
                    "--distribution-policy-query",
                    "three phase audit policy",
                    "--distribution-decision",
                    "dogfood_only",
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
            cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_distribution_review"
            ]
            self.assertEqual(len(cards), 1)
            card = cards[0]
            review = card["policy_distribution_review"]
            resolution = card["policy_distribution_source_resolution"]
            self.assertEqual(resolution["resolution_basis"], "policy_query_unique_match")
            self.assertEqual(review["distribution_decision"], "dogfood_only")
            self.assertFalse(review["writes_performed"])
            self.assertEqual(review["policy_id"], "POLICY-three-phase-audit")
            self.assertFalse(
                (project_root / "src" / "jikuo" / "policy_templates").exists()
            )
            atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
            self.assertIn("CAP-POLICY-DISTRIBUTION-REVIEW-01", atom_ids)

    def test_policy_distribution_review_returns_candidates_when_query_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "distribution_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "policy_distribution_review",
                    "--project-root",
                    str(project_root),
                    "--distribution-decision",
                    "deferred",
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
            cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_distribution_source_resolution"
            ]
            self.assertEqual(len(cards), 1)
            resolution = cards[0]["policy_distribution_source_resolution"]
            self.assertEqual(resolution["status"], "needs_policy_selection")
            self.assertIn("policy_ref_or_policy_query_required", resolution["refusal_reasons"])
            self.assertEqual(resolution["candidates"][0]["policy_id"], "POLICY-three-phase-audit")

    def test_policy_distribution_review_accepts_distribution_policy_ref_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "distribution_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "policy_distribution_review",
                    "--project-root",
                    str(project_root),
                    "--distribution-policy-ref",
                    "POLICY-three-phase-audit",
                    "--distribution-decision",
                    "optional_template",
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
            cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_distribution_review"
            ]
            self.assertEqual(len(cards), 1)
            resolution = cards[0]["policy_distribution_source_resolution"]
            review = cards[0]["policy_distribution_review"]
            self.assertEqual(resolution["resolution_basis"], "explicit_policy_ref")
            self.assertEqual(review["policy_id"], "POLICY-three-phase-audit")
            self.assertEqual(review["distribution_decision"], "optional_template")

    def test_policy_template_publication_plan_projects_guarded_apply_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "distribution_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)
            source_policy = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-three-phase-audit.yaml"
            )
            target_dir = Path(tmp) / "package_templates"

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "policy_template_publication_plan",
                    "--project-root",
                    str(project_root),
                    "--distribution-source-policy",
                    str(source_policy),
                    "--distribution-decision",
                    "optional_template",
                    "--distribution-source-project-ref",
                    "JIKUO-test",
                    "--publication-target-dir",
                    str(target_dir),
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
            cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_template_publication_plan"
            ]
            self.assertEqual(len(cards), 1)
            card = cards[0]
            plan = card["policy_template_publication_plan"]
            self.assertEqual(plan["schema"], "jikuo.policy_template_publication_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertFalse(plan["writes_performed"])
            self.assertEqual(plan["policy_id"], "POLICY-three-phase-audit")
            self.assertFalse(Path(plan["target_template_path"]).exists())
            command = card["command_proposal"]["command_preview"]
            self.assertIn("python -B -m jikuo.agent_flow", command)
            self.assertIn("policy_template_publication", command)
            self.assertNotIn("jikuo.policy_templates", command)
            atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
            self.assertIn("CAP-POLICY-TEMPLATE-PUBLICATION-PLAN-01", atom_ids)

    def test_apply_policy_template_publication_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "distribution_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)
            source_policy = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-three-phase-audit.yaml"
            )
            target_dir = Path(tmp) / "package_templates"

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_template_publication",
                    "--project-root",
                    str(project_root),
                    "--distribution-source-policy",
                    str(source_policy),
                    "--distribution-decision",
                    "optional_template",
                    "--distribution-source-project-ref",
                    "JIKUO-test",
                    "--publication-target-dir",
                    str(target_dir),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve publishing this policy as a package template.",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["operation"], "policy_template_publication")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.policy_template_publication_result.v0",
            )
            target = report["target_result"]
            self.assertEqual(target["status"], "written")
            self.assertTrue(Path(target["target_template_path"]).is_file())
            self.assertEqual(target["distribution_decision"], "optional_template")
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn(
                "CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-PUBLICATION-01",
                atom_ids,
            )

    def test_starter_manifest_publication_plan_projects_duplicate_refusal(self):
        template_ref = (
            "pkg://jikuo/policy_templates/engineering_governance/"
            "POLICYTEMPLATE-local-policy-task-scope-control-before-packaging.yaml"
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "starter_manifest_publication_plan",
                "--template-ref",
                template_ref,
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
        proposal = json.loads(completed.stdout)
        cards = [
            card
            for card in proposal["cards"]
            if card["card_kind"] == "starter_manifest_publication_plan"
        ]
        self.assertEqual(len(cards), 1)
        plan = cards[0]["starter_manifest_publication_plan"]
        self.assertEqual(
            plan["schema"],
            "jikuo.starter_pack_manifest_publication_plan.v0",
        )
        self.assertEqual(plan["status"], "refused")
        self.assertFalse(plan["writes_performed"])
        self.assertIn(
            "starter_pack_policy_id_already_present:POLICY-task-scope-control-before-packaging",
            plan["refusal_reasons"],
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-STARTER-MANIFEST-PUBLICATION-PLAN-01", atom_ids)

    def test_policy_template_import_plan_proposes_visible_guarded_activation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "template_project"
            project_root.mkdir()
            write_agent_flow_project_context(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "policy_template_import_plan",
                    "--template",
                    str(POLICY_TEMPLATE),
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
            proposal = json.loads(completed.stdout)
            self.assertEqual(proposal["status"], "review")
            self.assertTrue(proposal["approval_boundary"]["guarded_apply_available"])
            self.assertFalse(proposal["write_effect"]["writes_performed"])
            self.assertEqual(
                proposal["trigger_decision"]["invocation_scenario"],
                "policy_template_import_plan",
            )
            card = proposal["cards"][0]
            self.assertEqual(card["card_kind"], "policy_template_import_plan")
            self.assertEqual(card["status"], "review")
            plan = card["policy_template_import_plan"]
            self.assertEqual(plan["status"], "review")
            self.assertEqual(plan["project_context_status"], "present")
            self.assertEqual(
                {item["status"] for item in plan["binding_status"]},
                {"resolved"},
            )
            self.assertEqual(
                plan["resolved_policy"]["schema"],
                "jikuo.resolved_policy.v0",
            )
            command = card["command_proposal"]["command_preview"]
            self.assertIn("python -B -m jikuo.agent_flow", command)
            self.assertIn("policy_template_activation", command)
            self.assertIn("--confirm-apply", command)
            self.assertNotIn("jikuo.policy_templates", command)
            self.assertIn(
                "## Policy template import plan",
                proposal["chat_ready_markdown"],
            )
            atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
            self.assertIn("CAP-PROJECT-CONTEXT-RESOLVER-01", atom_ids)
            self.assertIn("CAP-POLICY-TEMPLATE-IMPORT-PLAN-01", atom_ids)
            self.assertIn(
                "CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01",
                atom_ids,
            )
            self.assertFalse((project_root / ".jikuo" / "policies").exists())

    def test_apply_policy_template_activation_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "template_project"
            project_root.mkdir()
            write_agent_flow_project_context(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_template_activation",
                    "--template",
                    str(POLICY_TEMPLATE),
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "policy_template_activation")
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.policy_template_activation_result.v0",
            )
            self.assertEqual(report["status"], "refused")
            self.assertFalse(report["write_performed"])
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-POLICY-TEMPLATE-ACTIVATE-01", atom_ids)
            self.assertIn(
                "CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01",
                atom_ids,
            )
            self.assertFalse((project_root / ".jikuo" / "policies").exists())

    def test_apply_policy_template_activation_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "template_project"
            project_root.mkdir()
            write_agent_flow_project_context(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_template_activation",
                    "--template",
                    str(POLICY_TEMPLATE),
                    "--project-root",
                    str(project_root),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve activating this reusable policy template.",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "policy_template_activation")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.policy_template_activation_result.v0",
            )
            target = report["target_result"]
            self.assertEqual(target["status"], "written")
            self.assertEqual(
                target["policy_ref"],
                "POLICY-task-scope-control-before-packaging",
            )
            self.assertTrue(target["post_write_verification"]["policy_active"])
            approved_path = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-task-scope-control-before-packaging.yaml"
            )
            self.assertTrue(approved_path.is_file())
            approved_text = approved_path.read_text(encoding="utf-8")
            self.assertIn("resolved_bindings:", approved_text)
            self.assertIn("pkg://jikuo/policy_templates/", approved_text)
            self.assertNotIn("NarrativeSystem", approved_text)
            self.assertIn(
                "## Target Result",
                report["chat_ready_markdown"],
            )

    def test_apply_policy_evolution_write_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_store_active_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_copy)
            manifest_file = project_copy / ".jikuo" / "policies" / "manifest.yaml"
            before_text = manifest_file.read_text(encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_evolution_write",
                    "--project-root",
                    str(project_copy),
                    "--policy-ref",
                    "POLICY-three-phase-audit",
                    "--policy-evolution-operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--policy-source-ref",
                    "User asked agent_flow apply to supersede the broad three-phase policy.",
                    "--replacement-policy-ref",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-trigger-event",
                    "conversation_turn",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "policy_evolution_write")
            self.assertFalse(report["write_performed"])
            self.assertEqual(report["status"], "refused")
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertIn(
                "proposal_ref_required_for_policy_evolution_apply",
                report["refusal_reasons"],
            )
            self.assertEqual(report["proposal_binding"]["status"], "missing")
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-POLICY-EVOLUTION-APPLY-BINDING-01", atom_ids)
            self.assertIn("CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01", atom_ids)
            self.assertEqual(manifest_file.read_text(encoding="utf-8"), before_text)

    def test_apply_policy_evolution_write_refuses_mismatched_proposal_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_store_active_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_copy)
            manifest_file = project_copy / ".jikuo" / "policies" / "manifest.yaml"
            before_text = manifest_file.read_text(encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_evolution_write",
                    "--project-root",
                    str(project_copy),
                    "--policy-ref",
                    "POLICY-three-phase-audit",
                    "--proposal-ref",
                    ".jikuo/policies/proposals/POLICYEVOPROPOSAL-not-approved.yaml",
                    "--policy-evolution-operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--policy-source-ref",
                    "User approved agent_flow apply supersession for the broad three-phase policy.",
                    "--replacement-policy-ref",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-trigger-event",
                    "conversation_turn",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
                    "--replacement-changed-path-pattern",
                    "docs/jikuo/**",
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve agent_flow applying this policy supersession.",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["status"], "refused")
            self.assertFalse(report["write_performed"])
            self.assertIn(
                "proposal_ref_mismatch_for_policy_evolution_apply",
                report["refusal_reasons"],
            )
            self.assertEqual(report["proposal_binding"]["status"], "mismatch")
            self.assertEqual(
                report["proposal_binding"]["provided_ref"],
                ".jikuo/policies/proposals/POLICYEVOPROPOSAL-not-approved.yaml",
            )
            self.assertNotEqual(
                report["proposal_binding"]["provided_ref"],
                report["proposal_binding"]["expected_ref"],
            )
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-POLICY-EVOLUTION-APPLY-BINDING-01", atom_ids)
            self.assertEqual(manifest_file.read_text(encoding="utf-8"), before_text)

    def test_apply_policy_evolution_write_supersedes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_store_active_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_copy)
            plan = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "plan-evolution",
                    "--project-root",
                    str(project_copy),
                    "--policy-id",
                    "POLICY-three-phase-audit",
                    "--operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--source-ref",
                    "User approved agent_flow apply supersession for the broad three-phase policy.",
                    "--replacement-policy-id",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-trigger-event",
                    "conversation_turn",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
                    "--replacement-changed-path-pattern",
                    "docs/jikuo/**",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(plan.returncode, 0, plan.stderr)
            proposal_ref = json.loads(plan.stdout)["proposal_ref"]
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_evolution_write",
                    "--project-root",
                    str(project_copy),
                    "--policy-ref",
                    "POLICY-three-phase-audit",
                    "--proposal-ref",
                    proposal_ref,
                    "--policy-evolution-operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--policy-source-ref",
                    "User approved agent_flow apply supersession for the broad three-phase policy.",
                    "--replacement-policy-ref",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-trigger-event",
                    "conversation_turn",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
                    "--replacement-changed-path-pattern",
                    "docs/jikuo/**",
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve agent_flow applying this policy supersession.",
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
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "policy_evolution_write")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(report["proposal_binding"]["status"], "ok")
            self.assertEqual(report["proposal_binding"]["provided_ref"], proposal_ref)
            self.assertEqual(report["proposal_binding"]["expected_ref"], proposal_ref)
            self.assertEqual(report["target_result_schema"], "jikuo.policy_write_result.v0")
            target = report["target_result"]
            self.assertEqual(target["status"], "written")
            self.assertEqual(target["operation"], "supersede_policy")
            self.assertEqual(target["proposal_ref"], proposal_ref)
            self.assertEqual(
                target["replacement_policy_ref"],
                "POLICY-three-phase-audit-agent-flow-v2",
            )
            self.assertIn(
                ".jikuo/policies/approved/POLICY-three-phase-audit-agent-flow-v2.yaml",
                target["written_paths"],
            )
            self.assertTrue(target["post_write_verification"]["target_policy_superseded"])
            self.assertTrue(target["post_write_verification"]["replacement_policy_active"])
            replacement_policy = (
                project_copy
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-three-phase-audit-agent-flow-v2.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn('event: "conversation_turn"', replacement_policy)

            status = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "status",
                    "--project-root",
                    str(project_copy),
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
            status_report = json.loads(status.stdout)
            self.assertEqual(
                status_report["active_policy_refs"][0]["policy_id"],
                "POLICY-three-phase-audit-agent-flow-v2",
            )
            self.assertEqual(
                status_report["superseded_policy_refs"][0]["policy_id"],
                "POLICY-three-phase-audit",
            )

            evaluation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "evaluate",
                    "--event",
                    "conversation_turn",
                    "--project-root",
                    str(project_copy),
                    "--task-type",
                    "work_order_delivery",
                    "--jikuo-layer",
                    "testing_governance",
                    "--changed-path",
                    "docs/jikuo/example.md",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(evaluation.returncode, 0, evaluation.stderr)
            eval_report = json.loads(evaluation.stdout)
            self.assertEqual(len(eval_report["triggered_policies"]), 1)
            self.assertEqual(
                eval_report["triggered_policies"][0]["policy_ref"],
                "POLICY-three-phase-audit-agent-flow-v2",
            )

    def test_policy_evidence_check_ingests_persisted_session_evidence_without_write(self):
        session_file = (
            POLICY_EVIDENCE_INGEST_PROJECT
            / ".jikuo"
            / "task_sessions"
            / "task_policy_evidence_probe.yaml"
        )
        before_text = session_file.read_text(encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evidence_check",
                "--policy-event",
                "task_start",
                "--session-id",
                "task_policy_evidence_probe",
                "--project-root",
                str(POLICY_EVIDENCE_INGEST_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_evidence_check",
        )
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "evaluated")
        self.assertEqual(
            proposal["policy_context"]["policy_evidence_check_status"],
            "checked",
        )
        self.assertEqual(
            proposal["policy_context"]["task_session_id"],
            "task_policy_evidence_probe",
        )
        self.assertEqual(
            proposal["policy_context"]["evidence_source_refs"],
            [".jikuo/task_sessions/task_policy_evidence_probe.yaml"],
        )
        self.assertEqual(len(proposal["evidence_status"]), 1)
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            proposal["evidence_status"][0]["evidence_refs"],
            ["EVD-persisted-card"],
        )
        self.assertEqual(proposal["missing_evidence_reports"], [])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-EVIDENCE-INGEST-01", atom_ids)
        self.assertIn("CAP-POLICY-EVIDENCE-CHECK-01", atom_ids)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_task_start_with_matching_policy_conditions_projects_condition_reports(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Condition Probe",
                "--project-root",
                str(POLICY_CONDITION_PROJECT),
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "configurable_rule_kernel",
                "--changed-path",
                "docs/jikuo/work_orders/SPRINT_050_probe.md",
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["policy_context"]["policy_condition_eval_status"],
            "checked",
        )
        self.assertEqual(len(proposal["condition_reports"]), 3)
        self.assertEqual(
            {item["status"] for item in proposal["condition_reports"]},
            {"matched"},
        )
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-work-order-condition-audit",
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-CONDITION-EVALUATOR-01", atom_ids)
        self.assertFalse((POLICY_CONDITION_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_policy_dead_zone_classifies_task_context_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "condition_project"
            shutil.copytree(POLICY_CONDITION_PROJECT, project_root)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Mismatched Context Probe",
                    "--project-root",
                    str(project_root),
                    "--task-type",
                    "analysis",
                    "--jikuo-layer",
                    "design_review",
                    "--changed-path",
                    "docs/jikuo/work_orders/SPRINT_050_probe.md",
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
            runtime_cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_runtime_status"
            ]
            self.assertEqual(len(runtime_cards), 1)
            runtime_card = runtime_cards[0]
            runtime_status = runtime_card["policy_runtime_status"]
            dead_zone = runtime_status["policy_dead_zone"]
            self.assertEqual(dead_zone["schema"], "jikuo.policy_dead_zone_classification.v0")
            self.assertEqual(dead_zone["classification"], "missing_or_mismatched_task_context")
            self.assertEqual(dead_zone["severity"], "warning")
            self.assertEqual(dead_zone["event"], "task_start")
            self.assertEqual(dead_zone["task_type"], "analysis")
            self.assertIn("task_type analysis did not match", dead_zone["reason"])
            self.assertEqual(runtime_card["status"], "review")
            self.assertIn(
                "policy_dead_zone: missing_or_mismatched_task_context",
                proposal["chat_ready_markdown"],
            )

    def test_task_start_projects_real_chain_policy_missing_evidence_and_feedback(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Real Chain Policy Probe",
                "--project-root",
                str(POLICY_REAL_CHAIN_PROJECT),
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "testing_governance",
                "--changed-path",
                "tools/jikuo/policy_store_tests.py",
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(
            proposal["policy_context"]["policy_condition_eval_status"],
            "checked",
        )
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-real-test-data-and-chain",
        )
        self.assertEqual(
            proposal["required_actions"][0]["action_type"],
            "verify_real_test_data_and_real_chain",
        )
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "missing")
        self.assertEqual(
            proposal["missing_evidence_reports"][0]["missing"][0]["required_type"],
            "real_test_data_and_chain_evidence",
        )
        feedback_by_type = {
            item["feedback_type"]: item for item in proposal["policy_feedback_options"]
        }
        self.assertEqual(
            set(feedback_by_type),
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertEqual(
            feedback_by_type["defer"]["missing_evidence_types"],
            ["real_test_data_and_chain_evidence"],
        )
        self.assertEqual(feedback_by_type["defer"]["missing_evidence_count"], 1)
        self.assertFalse(
            (POLICY_REAL_CHAIN_PROJECT / ".jikuo" / "task_sessions").exists()
        )

    def test_task_start_projects_real_chain_policy_ok_with_inline_evidence(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Real Chain Evidence Probe",
                "--project-root",
                str(POLICY_REAL_CHAIN_PROJECT),
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "testing_governance",
                "--changed-path",
                "tools/jikuo/policy_store_tests.py",
                "--produced-evidence-id",
                "EVD-real-chain-agent-flow",
                "--produced-evidence-type",
                "real_test_data_and_chain_evidence",
                "--produced-evidence-action-type",
                "verify_real_test_data_and_real_chain",
                "--produced-evidence-summary",
                "agent_flow used concrete fixture data through the policy evaluator path",
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
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-real-test-data-and-chain",
        )
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            proposal["evidence_status"][0]["evidence_refs"],
            ["EVD-real-chain-agent-flow"],
        )
        self.assertEqual(proposal["missing_evidence_reports"], [])
        self.assertEqual(
            {item["feedback_type"] for item in proposal["policy_feedback_options"]},
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertFalse(
            (POLICY_REAL_CHAIN_PROJECT / ".jikuo" / "task_sessions").exists()
        )

    def test_task_start_requires_explicit_core_debug_path_for_self_bootstrap_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)
            write_self_bootstrap_mcp_user_boundary_policy_store(project_root)

            base_args = [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Self-bootstrap path evidence probe",
                "--project-root",
                str(project_root),
                "--task-type",
                "jikuo_development",
                "--jikuo-layer",
                "policy_governance",
                "--changed-path",
                "src/jikuo/agent_flow.py",
                "--added-path",
                "docs/work_orders/self-bootstrap.md",
                "--format",
                "json",
            ]
            missing = subprocess.run(
                base_args,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(missing.returncode, 0, missing.stderr)
            missing_proposal = json.loads(missing.stdout)
            self.assertEqual(len(missing_proposal["triggered_policies"]), 1)
            self.assertEqual(
                missing_proposal["missing_evidence_reports"][0]["missing"][0][
                    "required_type"
                ],
                "jikuo_mcp_or_core_debug_path_evidence",
            )

            satisfied = subprocess.run(
                [*base_args[:-2], "--governance-path", "core_debug", "--format", "json"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(satisfied.returncode, 0, satisfied.stderr)
            proposal = json.loads(satisfied.stdout)
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
            self.assertEqual(
                proposal["evidence_status"][0]["required_type"],
                "jikuo_mcp_or_core_debug_path_evidence",
            )
            self.assertIn(
                "explicitly labelled core debug path",
                proposal["evidence_status"][0]["summary"],
            )

    def test_task_start_records_taskmap_insight_followup_distinction_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)
            write_taskmap_distinction_policy_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Taskmap Evidence Probe",
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
            proposal = json.loads(completed.stdout)
            self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
            self.assertEqual(proposal["work_routing"]["category"], "taskmap")
            self.assertEqual(
                proposal["work_routing"]["taskmap_items"],
                ["Taskmap Evidence Probe"],
            )
            self.assertIn("## Work Routing Evidence", proposal["chat_ready_markdown"])
            self.assertEqual(len(proposal["triggered_policies"]), 1)
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertEqual(
                proposal["evidence_status"][0]["required_type"],
                "taskmap_insight_followup_distinction_evidence",
            )
            self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
            self.assertIn(
                "CAP-TASKMAP-INSIGHT-FOLLOWUP-EVIDENCE-01",
                {trace["atom_id"] for trace in proposal["atom_trace"]},
            )

    def test_task_start_records_task_session_binding_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)
            write_task_session_binding_policy_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Task Session Binding Probe",
                    "--project-root",
                    str(project_root),
                    "--task-type",
                    "code_change",
                    "--jikuo-layer",
                    "implementation_governance",
                    "--changed-path",
                    "src/jikuo/agent_flow.py",
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
            self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
            self.assertEqual(
                proposal["triggered_policies"][0]["policy_ref"],
                "POLICY-jikuo-task-session-binding-at-slice-start",
            )
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertEqual(
                proposal["evidence_status"][0]["required_type"],
                "task_session_binding_evidence",
            )
            self.assertEqual(
                proposal["evidence_status"][0]["current_status"],
                "needs_user_decision",
            )
            atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
            self.assertIn("CAP-TASK-SESSION-BINDING-EVIDENCE-01", atom_ids)
            self.assertTrue(
                proposal["approval_boundary"]["guarded_apply_available"]
            )
            session_card = next(
                card
                for card in proposal["cards"]
                if card["card_kind"] == "task_session_start_preview"
            )
            command = session_card["command_proposal"]["command_preview"]
            self.assertEqual(
                session_card["task_session_resolution"]["status"],
                "needs_user_decision",
            )
            self.assertIn("python -B -m jikuo.agent_flow apply", command)
            self.assertIn("--operation \"task_session_start\"", command)
            self.assertIn("--confirm-apply", command)
            self.assertIn("--approval-phrase", command)
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_task_start_policy_triggers_for_document_governance_slice(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)
            write_task_session_binding_policy_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Document Governance Binding Probe",
                    "--project-root",
                    str(project_root),
                    "--task-type",
                    "documentation_registry_update",
                    "--jikuo-layer",
                    "document_governance",
                    "--changed-path",
                    "docs/governance/jikuo_productization_task_map.md",
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
            self.assertEqual(
                proposal["triggered_policies"][0]["policy_ref"],
                "POLICY-jikuo-task-session-binding-at-slice-start",
            )
            self.assertEqual(proposal["condition_reports"], [])
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertEqual(
                proposal["evidence_status"][0]["current_status"],
                "needs_user_decision",
            )

    def test_task_start_policy_accepts_explicit_task_session_deferral(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)
            write_task_session_binding_policy_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Explicit Deferral Probe",
                    "--project-root",
                    str(project_root),
                    "--task-session-decision",
                    "defer",
                    "--task-session-defer-reason",
                    "lightweight design discussion only",
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
            self.assertEqual(proposal["cards"][0]["card_kind"], "task_start_processing")
            self.assertEqual(proposal["cards"][1]["card_kind"], "task_session_binding")
            self.assertEqual(
                proposal["cards"][1]["task_session_resolution"]["status"],
                "explicitly_deferred",
            )
            self.assertEqual(
                proposal["evidence_status"][0]["current_status"],
                "explicitly_deferred",
            )
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_task_start_binds_existing_task_session_as_policy_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            create_agent_flow_ready_project(project_root)
            write_task_session_binding_policy_store(project_root)
            completed_create = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "task_session_start",
                    "--task-title",
                    "Existing Binding Probe",
                    "--project-root",
                    str(project_root),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve this task-session start through agent_flow.",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed_create.returncode, 0, completed_create.stderr)
            created_report = json.loads(completed_create.stdout)
            session_id = created_report["target_result"]["session_id"]

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Existing Binding Probe",
                    "--session-id",
                    session_id,
                    "--project-root",
                    str(project_root),
                    "--task-type",
                    "code_change",
                    "--jikuo-layer",
                    "implementation_governance",
                    "--changed-path",
                    "src/jikuo/agent_flow.py",
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
            self.assertEqual(proposal["cards"][0]["card_kind"], "task_start_processing")
            session_card = next(
                card
                for card in proposal["cards"]
                if card["card_kind"] == "task_session_binding"
            )
            self.assertEqual(session_card["status"], "ok")
            self.assertIsNone(session_card.get("command_proposal"))
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertEqual(
                proposal["evidence_status"][0]["required_type"],
                "task_session_binding_evidence",
            )
            self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
            atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
            self.assertIn("CAP-TASK-STATUS-01", atom_ids)
            self.assertIn("CAP-TASK-SESSION-BINDING-EVIDENCE-01", atom_ids)

    def test_completion_review_policy_evidence_surfaces_without_task_session_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_main_doc_mount_policy_store(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "completion_review",
                    "--session-id",
                    "missing_session_for_policy_only_review",
                    "--task-title",
                    "Completion Review Probe",
                    "--project-root",
                    str(project_root),
                    "--summary",
                    "Checked main document mount scope before completion.",
                    "--produced-evidence-id",
                    "EVD-main-doc-review",
                    "--produced-evidence-type",
                    "main_document_mount_maintenance_evidence",
                    "--produced-evidence-action-type",
                    "maintain_main_document_mounts_and_update_scope_before_completion",
                    "--produced-evidence-summary",
                    "Checked main document mounts before slice completion.",
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
            self.assertEqual(proposal["status"], "review")
            self.assertEqual(proposal["trigger_decision"]["execution_readiness"], "ready")
            self.assertEqual(proposal["trigger_decision"]["required_clarification"], [])
            self.assertEqual(
                proposal["triggered_policies"][0]["policy_ref"],
                "POLICY-jikuo-main-doc-mount-maintenance",
            )
            self.assertEqual(proposal["missing_evidence_reports"], [])
            self.assertEqual(
                proposal["evidence_status"][0]["required_type"],
                "main_document_mount_maintenance_evidence",
            )
            self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")

            lifecycle_cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "task_session_lifecycle_unavailable"
            ]
            self.assertEqual(len(lifecycle_cards), 1)
            self.assertEqual(lifecycle_cards[0]["status"], "review")
            self.assertIn(
                "task_sessions_root_missing",
                lifecycle_cards[0]["refusal_reasons"],
            )

            runtime_cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_runtime_status"
            ]
            self.assertEqual(len(runtime_cards), 1)
            self.assertEqual(runtime_cards[0]["status"], "ok")
            self.assertEqual(
                runtime_cards[0]["policy_runtime_status"]["missing_evidence_count"],
                0,
            )
            self.assertEqual(proposal["runtime_visibility"]["status"], "ok")
            self.assertEqual(proposal["client_display_links"]["status"], "available")
            self.assertTrue(
                (project_root / ".jikuo" / "runtime" / "last_card.md").is_file()
            )
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_completion_review_projects_artifact_assurance_into_runtime_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_agent_flow_document_mount_project_context(project_root)
            produced_evidence = [
                {
                    "evidence_id": "read-project-context",
                    "evidence_type": "document_read_evidence",
                    "path": ".jikuo/project_context.yaml",
                    "summary": "read configured project context",
                },
                {
                    "evidence_id": "read-execution-mounts",
                    "evidence_type": "document_read_evidence",
                    "path": "docs/governance.md",
                    "summary": "read active mount authority",
                },
                {
                    "evidence_id": "read-required-context",
                    "evidence_type": "document_read_evidence",
                    "path": "docs/required.md",
                    "summary": "read required document role",
                },
                {
                    "evidence_id": "plan-main-doc",
                    "evidence_type": "document_write_plan_evidence",
                    "path": "docs/main.md",
                    "summary": "planned main document maintenance",
                },
                {
                    "evidence_id": "write-main-doc",
                    "evidence_type": "document_write_evidence",
                    "path": "docs/main.md",
                    "summary": "updated main document maintenance",
                },
            ]

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "completion_review",
                    "--task-title",
                    "Artifact Assurance Probe",
                    "--project-root",
                    str(project_root),
                    "--summary",
                    "Completion card should persist document read/write assurance.",
                    "--produced-evidence-json",
                    json.dumps(produced_evidence),
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
            assurance = proposal["artifact_assurance"]
            self.assertEqual(assurance["status"], "ok")
            self.assertEqual(
                assurance["runtime_projection"]["persistence"],
                "runtime_card_and_state_summary",
            )
            self.assertEqual(assurance["gap_report"]["gap_count"], 0)
            self.assertIn("## Artifact Assurance", proposal["chat_ready_markdown"])
            self.assertIn("- Required reads: `3`", proposal["chat_ready_markdown"])
            self.assertIn("- Read evidence: `3`", proposal["chat_ready_markdown"])
            self.assertIn("- Completion-check documents: `1`", proposal["chat_ready_markdown"])
            self.assertIn("- Completion-check documents not evaluated: `0`", proposal["chat_ready_markdown"])
            self.assertIn("- Applicable required writes: `1`", proposal["chat_ready_markdown"])
            self.assertIn("- Planned writes: `1`", proposal["chat_ready_markdown"])
            self.assertIn("- Actual writes: `1`", proposal["chat_ready_markdown"])
            self.assertIn("- Gap count: `0`", proposal["chat_ready_markdown"])

            state_summary = json.loads(
                (project_root / ".jikuo" / "runtime" / "state_summary.json").read_text(
                    encoding="utf-8",
                )
            )
            self.assertEqual(state_summary["artifact_assurance"]["status"], "ok")
            self.assertEqual(
                state_summary["artifact_assurance"]["gap_report"]["gap_count"],
                0,
            )
            history_ref = proposal["runtime_visibility"]["history_ref"]
            history_text = (project_root / history_ref).read_text(encoding="utf-8")
            self.assertIn("## Artifact Assurance", history_text)

    def test_completion_review_artifact_assurance_surfaces_write_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_agent_flow_document_mount_project_context(project_root)
            produced_evidence = [
                {
                    "evidence_id": "plan-main-doc",
                    "evidence_type": "document_write_plan_evidence",
                    "path": "docs/main.md",
                    "summary": "planned main document maintenance",
                },
            ]

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "completion_review",
                    "--task-title",
                    "Artifact Assurance Gap Probe",
                    "--project-root",
                    str(project_root),
                    "--changed-path",
                    "docs/unrelated.md",
                    "--produced-evidence-json",
                    json.dumps(produced_evidence),
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
            assurance = proposal["artifact_assurance"]
            self.assertEqual(assurance["status"], "review")
            self.assertEqual(assurance["gap_report"]["write_gap_count"], 3)
            self.assertEqual(
                assurance["write_assurance"]["required_not_written"][0]["path"],
                "docs/main.md",
            )
            self.assertEqual(
                assurance["write_assurance"]["planned_not_written"][0]["path"],
                "docs/main.md",
            )
            self.assertEqual(
                assurance["write_assurance"]["unplanned_written"][0]["path"],
                "docs/unrelated.md",
            )
            self.assertIn("`required_write_not_observed` / `docs/main.md`", proposal["chat_ready_markdown"])
            self.assertIn("`planned_write_not_observed` / `docs/main.md`", proposal["chat_ready_markdown"])
            self.assertIn("`actual_write_not_planned` / `docs/unrelated.md`", proposal["chat_ready_markdown"])

    def test_completion_review_uses_git_observed_actual_writes_when_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_agent_flow_document_mount_project_context(project_root)
            initialize_git_repo(project_root)
            commit_project_baseline(project_root)
            (project_root / "docs" / "unreported.md").write_text(
                "real write not declared\n",
                encoding="utf-8",
            )
            produced_evidence = [
                {
                    "evidence_id": "plan-main-doc",
                    "evidence_type": "document_write_plan_evidence",
                    "path": "docs/main.md",
                    "summary": "planned main document maintenance",
                },
            ]

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "completion_review",
                    "--task-title",
                    "Git Actual Write Probe",
                    "--project-root",
                    str(project_root),
                    "--produced-evidence-json",
                    json.dumps(produced_evidence),
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
            assurance = proposal["artifact_assurance"]
            runtime_projection = assurance["runtime_projection"]
            git_observation = runtime_projection["git_write_observation"]
            self.assertEqual(runtime_projection["actual_write_source"], "git_status_observed")
            self.assertEqual(runtime_projection["declared_actual_write_count"], 0)
            self.assertEqual(git_observation["status"], "ok")
            self.assertEqual(git_observation["observed_actual_write_paths"], ["docs/unreported.md"])
            self.assertEqual(
                assurance["write_assurance"]["actual_write_set"][0]["source_kind"],
                "git_diff",
            )
            self.assertEqual(
                assurance["write_assurance"]["unplanned_written"][0]["path"],
                "docs/unreported.md",
            )
            atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
            self.assertIn("CAP-RUNTIME-WRITE-OBSERVATION-COMPLETION-REVIEW-01", atom_ids)
            self.assertIn("- Actual write source: `git_status_observed`", proposal["chat_ready_markdown"])
            self.assertIn("`actual_write_not_planned` / `docs/unreported.md`", proposal["chat_ready_markdown"])

    def test_completion_review_unappraised_candidates_do_not_emit_required_write_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_agent_flow_document_mount_project_context(project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "completion_review",
                    "--task-title",
                    "Artifact Assurance Candidate Probe",
                    "--project-root",
                    str(project_root),
                    "--changed-path",
                    "docs/unrelated.md",
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
            assurance = proposal["artifact_assurance"]
            write = assurance["write_assurance"]
            self.assertEqual(assurance["status"], "review")
            self.assertEqual(write["completion_check_candidate_count"], 1)
            self.assertEqual(len(write["completion_check_not_evaluated"]), 1)
            self.assertEqual(write["required_write_count"], 0)
            self.assertEqual(write["required_not_written"], [])
            self.assertEqual(assurance["gap_report"]["gap_count"], 0)
            self.assertIn("- Completion-check documents: `1`", proposal["chat_ready_markdown"])
            self.assertIn("- Applicable required writes: `0`", proposal["chat_ready_markdown"])
            self.assertNotIn("`required_write_not_observed`", proposal["chat_ready_markdown"])

    def test_task_start_projects_pre_code_change_classification_policy(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Pre Code Classification Probe",
                "--project-root",
                str(POLICY_REAL_CHAIN_PROJECT),
                "--task-type",
                "code_change",
                "--jikuo-layer",
                "implementation_governance",
                "--changed-path",
                "tools/jikuo/policy_store.py",
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
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-pre-code-change-layer-classification",
        )
        self.assertEqual(
            proposal["required_actions"][0]["action_type"],
            "classify_governance_vs_implementation_before_code_change",
        )
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "missing")
        self.assertEqual(
            proposal["missing_evidence_reports"][0]["missing"][0]["required_type"],
            "governance_vs_implementation_classification_evidence",
        )
        self.assertEqual(
            {item["feedback_type"] for item in proposal["policy_feedback_options"]},
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertFalse(
            (POLICY_REAL_CHAIN_PROJECT / ".jikuo" / "task_sessions").exists()
        )

    def test_policy_write_plan_projects_no_write_card(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_write_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-title",
                "Three-phase task audit",
                "--policy-source-ref",
                "<exact user phrase as spoken>",
                "--policy-task-type",
                "work_order_delivery",
                "--policy-jikuo-layer",
                "configurable_rule_kernel",
                "--policy-changed-path-pattern",
                "docs/jikuo/**",
                "--policy-work-profile-lifecycle-event",
                "task_start",
                "--policy-work-profile-policy-scope",
                "discussion",
                "--policy-work-profile-policy-scope",
                "editing",
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
        proposal = json.loads(completed.stdout)
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_write_plan",
        )
        self.assertEqual(proposal["cards"][0]["card_kind"], "policy_write_plan")
        plan = proposal["cards"][0]["policy_write_plan"]
        self.assertEqual(plan["schema"], "jikuo.policy_write_plan.v0")
        self.assertEqual(plan["status"], "review")
        self.assertEqual(plan["policy_ref"], "POLICY-three-phase-audit")
        self.assertEqual(len(plan["proposed_policy"]["conditions"]), 3)
        self.assertEqual(
            plan["proposed_policy"]["applies_to_work_profile"],
            [
                {
                    "lifecycle_events": ["task_start"],
                    "policy_scopes": ["discussion", "editing"],
                }
            ],
        )
        self.assertEqual(
            plan["write_set"][0]["path"],
            ".jikuo/policies/approved/POLICY-three-phase-audit.yaml",
        )
        command = proposal["cards"][0]["command_proposal"]
        self.assertTrue(command["approval_required"])
        self.assertTrue(command["technical_confirmation_required"])
        self.assertIn("python -B -m jikuo.policy_store", command["command_preview"])
        self.assertNotIn("tools/jikuo", command["command_preview"])
        self.assertIn("write-policy", command["command_preview"])
        self.assertIn("--confirm-write-policy", command["command_preview"])
        self.assertIn("--approval-phrase", command["command_preview"])
        self.assertIn("--work-profile-lifecycle-event", command["command_preview"])
        self.assertIn("--work-profile-policy-scope", command["command_preview"])
        self.assertIn(
            "work_profile_lifecycle_events: task_start",
            proposal["cards"][0]["shown_inputs"],
        )
        self.assertIn(
            "work_profile_policy_scopes: discussion, editing",
            proposal["cards"][0]["shown_inputs"],
        )
        self.assertIn(
            "authoring_mode: lifecycle_gated",
            proposal["cards"][0]["shown_inputs"],
        )
        self.assertIn(
            "authoring_warning: lifecycle_events_hard_gate_policy_applicability",
            proposal["cards"][0]["shown_outputs"],
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-STORE-WRITE-PROPOSE-01", atom_ids)
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_policy_write_plan_projects_scope_only_conversation_turn_card(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_write_plan",
                "--policy-ref",
                "POLICY-intent-scope-review",
                "--policy-title",
                "Intent scope review",
                "--policy-source-ref",
                "<exact user phrase as spoken>",
                "--policy-trigger-event",
                "conversation_turn",
                "--policy-work-profile-policy-scope",
                "discussion",
                "--policy-action-type",
                "perform_intent_scope_review",
                "--policy-evidence-type",
                "intent_scope_review_evidence",
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
        proposal = json.loads(completed.stdout)
        plan = proposal["cards"][0]["policy_write_plan"]
        self.assertEqual(
            plan["proposed_policy"]["triggers"][0]["event"],
            "conversation_turn",
        )
        self.assertEqual(
            plan["proposed_policy"]["applies_to_work_profile"],
            [
                {
                    "lifecycle_events": [],
                    "policy_scopes": ["discussion"],
                }
            ],
        )
        command = proposal["cards"][0]["command_proposal"]
        self.assertIn('--trigger-event "conversation_turn"', command["command_preview"])
        self.assertIn("--work-profile-policy-scope", command["command_preview"])
        self.assertNotIn("--work-profile-lifecycle-event", command["command_preview"])
        self.assertIn(
            "work_profile_policy_scopes: discussion",
            proposal["cards"][0]["shown_inputs"],
        )
        self.assertIn(
            "authoring_mode: scope_only",
            proposal["cards"][0]["shown_inputs"],
        )
        self.assertIn(
            "authoring_mode: scope_only",
            proposal["cards"][0]["shown_outputs"],
        )
        self.assertIn(
            "compatibility_trigger_event: conversation_turn",
            proposal["cards"][0]["shown_outputs"],
        )
        self.assertNotIn(
            "work_profile_lifecycle_events: task_start",
            proposal["cards"][0]["shown_inputs"],
        )
        self.assertNotIn(
            "authoring_warning: lifecycle_events_hard_gate_policy_applicability",
            proposal["cards"][0]["shown_outputs"],
        )

    def test_policy_dead_zone_classifies_policy_write_plan_as_non_governance(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "active_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_root)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "policy_write_plan",
                    "--policy-ref",
                    "POLICY-new-governance-rule",
                    "--policy-title",
                    "New governance rule",
                    "--policy-source-ref",
                    "<exact user phrase as spoken>",
                    "--policy-task-type",
                    "code_change",
                    "--policy-jikuo-layer",
                    "implementation_governance",
                    "--policy-changed-path-pattern",
                    "src/**",
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
            proposal = json.loads(completed.stdout)
            runtime_cards = [
                card
                for card in proposal["cards"]
                if card["card_kind"] == "policy_runtime_status"
            ]
            self.assertEqual(len(runtime_cards), 1)
            runtime_card = runtime_cards[0]
            runtime_status = runtime_card["policy_runtime_status"]
            dead_zone = runtime_status["policy_dead_zone"]
            self.assertEqual(dead_zone["classification"], "non_governance_event")
            self.assertEqual(dead_zone["severity"], "info")
            self.assertEqual(dead_zone["event"], "policy_write_plan")
            self.assertEqual(runtime_card["status"], "ok")
            self.assertIn(
                "do not treat this card as proof that task work was governed",
                dead_zone["next_actions"],
            )

    def test_starter_policy_pack_init_projects_agent_flow_apply_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "starter_project"
            project_root.mkdir()
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "initialize_jikuo",
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
            proposal = json.loads(completed.stdout)
            self.assertFalse(proposal["write_effect"]["writes_performed"])
            self.assertTrue(proposal["approval_boundary"]["guarded_apply_available"])
            self.assertEqual(
                proposal["trigger_decision"]["invocation_scenario"],
                "starter_policy_pack_init",
            )
            card = proposal["cards"][0]
            self.assertEqual(card["card_kind"], "starter_policy_pack_init_plan")
            plan = card["starter_policy_pack_init_plan"]
            self.assertEqual(plan["schema"], "jikuo.starter_policy_pack_init_plan.v0")
            self.assertTrue(plan["would_create_project_state"])
            self.assertEqual(len(plan["starter_policies"]), 4)
            runtime_cards = [
                item
                for item in proposal["cards"]
                if item["card_kind"] == "policy_runtime_status"
            ]
            self.assertEqual(len(runtime_cards), 1)
            runtime_status = runtime_cards[0]["policy_runtime_status"]
            self.assertEqual(runtime_status["policy_store_status"], "missing")
            self.assertEqual(runtime_status["active_policy_count"], 0)
            self.assertEqual(runtime_status["triggered_policy_count"], 0)
            command = card["command_proposal"]["command_preview"]
            self.assertIn("python -B -m jikuo.agent_flow", command)
            self.assertIn("apply", command)
            self.assertIn("--operation \"starter_policy_pack_init\"", command)
            self.assertIn("--confirm-apply", command)
            self.assertNotIn("tools/jikuo", command)
            self.assertTrue((project_root / ".jikuo" / "runtime").is_dir())
            self.assertFalse((project_root / ".jikuo" / "project_state.yaml").exists())
            self.assertFalse((project_root / ".jikuo" / "policies").exists())

    def test_policy_evolution_plan_projects_refinement_without_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evolution_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-evolution-operation",
                "refine_policy",
                "--feedback-type",
                "needs_scope_narrowing",
                "--summary",
                "Triggered for a task that should not require this review.",
                "--policy-source-ref",
                "<exact user phrase as spoken>",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_evolution_plan",
        )
        self.assertEqual(proposal["cards"][0]["card_kind"], "policy_evolution_plan")
        plan = proposal["cards"][0]["policy_evolution_plan"]
        self.assertEqual(plan["schema"], "jikuo.policy_evolution_plan.v0")
        self.assertEqual(plan["status"], "review")
        self.assertEqual(plan["target_policy_ref"], "POLICY-three-phase-audit")
        self.assertFalse(plan["writes_performed"])
        self.assertTrue(plan["future_write_boundary"]["writer_implemented"])
        command = proposal["cards"][0]["command_proposal"]
        self.assertTrue(command["approval_required"])
        self.assertIn("write-evolution", command["command_preview"])
        self.assertIn("--operation \"refine_policy\"", command["command_preview"])
        self.assertIn("--confirm-write-evolution", command["command_preview"])
        self.assertIn(
            ".jikuo/policies/approved/POLICY-three-phase-audit.yaml",
            command["writes_if_approved"],
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01", atom_ids)

    def test_policy_evolution_plan_projects_deprecation_command(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evolution_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-evolution-operation",
                "deprecate_policy",
                "--feedback-type",
                "not_applicable",
                "--summary",
                "Policy should stop triggering for this project.",
                "--policy-source-ref",
                "User asked to preview deprecating the three-phase audit policy for this project.",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        self.assertIn(
            "review policy evolution recommendation and any generated guarded command before approving a write",
            proposal["next_actions"],
        )
        card = proposal["cards"][0]
        self.assertEqual(card["card_kind"], "policy_evolution_plan")
        command = card["command_proposal"]
        self.assertTrue(command["approval_required"])
        self.assertTrue(command["technical_confirmation_required"])
        self.assertIn("python -B -m jikuo.policy_store", command["command_preview"])
        self.assertNotIn("tools/jikuo", command["command_preview"])
        self.assertIn("write-evolution", command["command_preview"])
        self.assertIn("--confirm-write-evolution", command["command_preview"])
        self.assertIn(".jikuo/policies/manifest.yaml", command["writes_if_approved"])

    def test_policy_evolution_plan_projects_supersession_command(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evolution_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-evolution-operation",
                "supersede_policy",
                "--feedback-type",
                "needs_scope_narrowing",
                "--summary",
                "Policy should be replaced with narrower conditions.",
                "--policy-source-ref",
                "User asked to preview replacing the broad three-phase audit policy with a narrower v2 policy.",
                "--replacement-policy-ref",
                "POLICY-three-phase-audit-v2",
                "--replacement-title",
                "Three-phase task audit v2",
                "--replacement-trigger-event",
                "conversation_turn",
                "--replacement-task-type",
                "work_order_delivery",
                "--replacement-jikuo-layer",
                "testing_governance",
                "--replacement-changed-path-pattern",
                "docs/jikuo/**",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        card = proposal["cards"][0]
        self.assertEqual(card["card_kind"], "policy_evolution_plan")
        plan = card["policy_evolution_plan"]
        self.assertEqual(plan["operation"], "supersede_policy")
        self.assertEqual(plan["replacement_policy_ref"], "POLICY-three-phase-audit-v2")
        self.assertEqual(
            plan["replacement_policy"]["triggers"][0]["event"],
            "conversation_turn",
        )
        self.assertTrue(plan["future_write_boundary"]["writer_implemented"])
        self.assertIn(
            ".jikuo/policies/approved/POLICY-three-phase-audit-v2.yaml",
            {item["path"] for item in plan["write_set"]},
        )
        command = card["command_proposal"]
        self.assertTrue(command["approval_required"])
        self.assertTrue(command["technical_confirmation_required"])
        self.assertIn("python -B -m jikuo.policy_store", command["command_preview"])
        self.assertNotIn("tools/jikuo", command["command_preview"])
        self.assertIn("write-evolution", command["command_preview"])
        self.assertIn("--operation \"supersede_policy\"", command["command_preview"])
        self.assertIn("--replacement-policy-id \"POLICY-three-phase-audit-v2\"", command["command_preview"])
        self.assertIn("--replacement-title \"Three-phase task audit v2\"", command["command_preview"])
        self.assertIn("--replacement-trigger-event \"conversation_turn\"", command["command_preview"])
        self.assertIn("--confirm-write-evolution", command["command_preview"])
        self.assertIn(
            ".jikuo/policies/approved/POLICY-three-phase-audit-v2.yaml",
            command["writes_if_approved"],
        )
        self.assertIn(".jikuo/policies/manifest.yaml", command["writes_if_approved"])


if __name__ == "__main__":
    unittest.main()
