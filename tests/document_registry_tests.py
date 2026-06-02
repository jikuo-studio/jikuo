import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_ROOT = ROOT / "docs" / "registry"
CAP_RE = re.compile(r"CAP-[A-Z0-9-]+")
ALLOWED_WORK_ORDER_CAPABILITY_EXTRACTION = {
    "extracted_from_work_order_body",
    "no_capability_refs_found",
}
ALLOWED_REVERSE_CACHE_FIELDS = {
    "referenced_by_transitional_cache",
    "referenced_by_transitional_cache_truncated",
}


def read_rel(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def quoted_values(text: str, key: str) -> list[str]:
    pattern = re.compile(rf"^\s*(?:-\s+)?{re.escape(key)}:\s+\"([^\"]+)\"", re.MULTILINE)
    return pattern.findall(text)


def entry_ids(text: str) -> list[str]:
    return quoted_values(text, "id")


def split_entries(text: str) -> list[str]:
    return re.split(r"(?=^  - id: )", text, flags=re.MULTILINE)[1:]


def block_values(text: str, key: str) -> list[str]:
    values: list[str] = []
    pattern = re.compile(
        rf"^\s+{re.escape(key)}:\n((?:\s+- \"[^\"]+\"\n)+)",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        values.extend(re.findall(r'- "([^"]+)"', match.group(1)))
    return values


def ref_path(value: str) -> str:
    return value.split("#", 1)[0]


def existing_rel(path: str) -> bool:
    return (ROOT / path).exists()


class DocumentRegistryTests(unittest.TestCase):
    def test_index_declares_existing_shards(self) -> None:
        index = read_rel("docs/registry/registry_index.yaml")
        for shard_path in quoted_values(index, "path"):
            if shard_path.startswith(("docs/registry/", "docs/insights/", ".jikuo/")):
                self.assertTrue(existing_rel(shard_path), shard_path)

    def test_registry_yaml_shards_are_indexed(self) -> None:
        index = read_rel("docs/registry/registry_index.yaml")
        indexed = {
            path
            for path in quoted_values(index, "path")
            if path.startswith("docs/registry/")
        }
        actual = {
            f"docs/registry/{path.name}"
            for path in REGISTRY_ROOT.glob("*.yaml")
            if path.name != "registry_index.yaml"
        }
        self.assertEqual(actual, indexed)

    def test_open_items_is_not_a_source_shard(self) -> None:
        index = read_rel("docs/registry/registry_index.yaml")
        self.assertIn('id: "open_items"', index)
        self.assertIn("Open items are a computed view", index)
        self.assertFalse(existing_rel("docs/registry/open_items.yaml"))

    def test_work_order_paths_exist(self) -> None:
        work_orders = read_rel("docs/registry/work_orders.yaml")
        paths = [
            value
            for value in quoted_values(work_orders, "path")
            if value.startswith("docs/work_orders/")
        ]
        self.assertGreaterEqual(len(paths), 80)
        for path in paths:
            self.assertTrue(existing_rel(path), path)

    def test_all_work_order_files_are_registered(self) -> None:
        work_orders = read_rel("docs/registry/work_orders.yaml")
        registered = {
            value
            for value in quoted_values(work_orders, "path")
            if value.startswith("docs/work_orders/")
        }
        actual = {
            f"docs/work_orders/{path.name}"
            for path in (ROOT / "docs" / "work_orders").glob("*.md")
        }
        self.assertEqual(actual, registered)

    def test_all_insight_files_are_registered(self) -> None:
        registry = read_rel("docs/insights/insights_registry.yaml")
        registered = {
            value
            for value in quoted_values(registry, "file")
            if value.startswith("docs/insights/INSIGHT-")
        }
        actual = {
            f"docs/insights/{path.name}"
            for path in (ROOT / "docs" / "insights").glob("INSIGHT-*.md")
        }
        self.assertEqual(actual, registered)
        for path in registered:
            self.assertTrue(existing_rel(path), path)

    def test_capability_ids_have_valid_prefix(self) -> None:
        capabilities = read_rel("docs/registry/capabilities.yaml")
        ids = entry_ids(capabilities)
        cap_ids = [value for value in ids if value.startswith("CAP-")]
        self.assertGreaterEqual(len(cap_ids), 100)
        self.assertEqual(len(cap_ids), len(set(cap_ids)))
        for cap_id in cap_ids:
            self.assertRegex(cap_id, r"^CAP-[A-Z0-9-]+$")

    def test_forward_refs_resolve(self) -> None:
        capabilities = read_rel("docs/registry/capabilities.yaml")
        cap_ids = set(CAP_RE.findall(capabilities))
        for shard in ("scenario_chains.yaml", "work_orders.yaml"):
            text = read_rel(f"docs/registry/{shard}")
            for cap_id in CAP_RE.findall(text):
                self.assertIn(cap_id, cap_ids, f"{cap_id} in {shard}")

        mount_sets = read_rel("docs/registry/mount_sets.yaml")
        for path in quoted_values(mount_sets, "path"):
            self.assertTrue(existing_rel(path), path)

    def test_work_order_context_anchors_resolve(self) -> None:
        work_orders = read_rel("docs/registry/work_orders.yaml")
        mount_sets = read_rel("docs/registry/mount_sets.yaml")
        mount_ids = set(entry_ids(mount_sets))
        for mount_id in block_values(work_orders, "required_mount_sets"):
            self.assertIn(mount_id, mount_ids, mount_id)
        for key in ("originating_evidence_refs", "authority_refs"):
            for value in block_values(work_orders, key):
                self.assertTrue(existing_rel(ref_path(value)), value)

    def test_poltrig_03_mounts_dead_zone_evidence(self) -> None:
        work_orders = read_rel("docs/registry/work_orders.yaml")
        entries = split_entries(work_orders)
        matches = [entry for entry in entries if 'id: "JIKUO-POLTRIG-03"' in entry]
        self.assertEqual(len(matches), 1)
        entry = matches[0]
        self.assertIn("MOUNT-POLICY-TRIGGER-DEAD-ZONE-REPAIR", entry)
        self.assertIn("LIVE-20_policy_dead_zone_detection.md#7-initial-evidence", entry)
        self.assertIn("jikuo_policy_governance_authority.md", entry)
        self.assertIn("Do not make intent_classes", entry)

    def test_scenario_chain_atom_registration_guide_is_registered_and_mounted(self) -> None:
        guide = "docs/governance/jikuo_scenario_chain_and_atom_registration_guide.md"
        context = read_rel(".jikuo/project_context.yaml")
        mount_sets = read_rel("docs/registry/mount_sets.yaml")
        index = read_rel("docs/registry/registry_index.yaml")
        docs_readme = read_rel("docs/README.md")

        self.assertTrue(existing_rel(guide), guide)
        self.assertIn(guide, context)
        self.assertIn(guide, mount_sets)
        self.assertIn("MOUNT-SCENARIO-CHAIN-ATOM-REGISTRATION", mount_sets)
        self.assertIn(guide, index)
        self.assertIn(guide, docs_readme)

    def test_registry_shards_do_not_hand_maintain_reverse_edges(self) -> None:
        reverse_field_re = re.compile(r"^\s+(used_by|referenced_by|source_work_orders|source_refs):", re.MULTILINE)
        for path in REGISTRY_ROOT.glob("*.yaml"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in reverse_field_re.finditer(text):
                field = match.group(1)
                self.assertIn(
                    field,
                    ALLOWED_REVERSE_CACHE_FIELDS,
                    f"{field} in {path.relative_to(ROOT)}",
                )

    def test_capability_metadata_and_transitional_cache_paths(self) -> None:
        capabilities = read_rel("docs/registry/capabilities.yaml")
        self.assertNotIn("source_refs:", capabilities)
        entries = split_entries(capabilities)
        self.assertGreaterEqual(len(entries), 100)
        allowed_metadata = {"complete", "metadata_missing_in_task_map"}

        for entry in entries:
            metadata = quoted_values(entry, "metadata_status")
            self.assertEqual(len(metadata), 1, entry[:160])
            self.assertIn(metadata[0], allowed_metadata)
            if 'status: "pending_review"' in entry:
                self.assertEqual(metadata[0], "metadata_missing_in_task_map")

        for path in block_values(capabilities, "referenced_by_transitional_cache"):
            self.assertTrue(existing_rel(path), path)

    def test_work_order_capability_extraction_status_matches_edges(self) -> None:
        work_orders = read_rel("docs/registry/work_orders.yaml")
        entries = split_entries(work_orders)
        self.assertGreaterEqual(len(entries), 80)
        for entry in entries:
            statuses = quoted_values(entry, "capability_extraction_status")
            self.assertEqual(len(statuses), 1, entry[:160])
            status = statuses[0]
            self.assertIn(status, ALLOWED_WORK_ORDER_CAPABILITY_EXTRACTION)
            refs = block_values(entry, "implements_capabilities")
            if status == "extracted_from_work_order_body":
                self.assertGreater(len(refs), 0, entry[:160])
            else:
                self.assertEqual(refs, [], entry[:160])
            self.assertNotIn("CAP-UNKNOWN", refs)

    def test_repo_cap_ids_are_registered_warning_only(self) -> None:
        capabilities = read_rel("docs/registry/capabilities.yaml")
        registered = set(CAP_RE.findall(capabilities))
        observed: set[str] = set()
        for base in (ROOT / "docs", ROOT / ".jikuo"):
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if path.suffix not in {".md", ".yaml", ".yml"}:
                    continue
                observed.update(CAP_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
        if (ROOT / "README.md").exists():
            observed.update(CAP_RE.findall(read_rel("README.md")))

        missing = sorted(observed - registered)
        if missing:
            print("WARNING: unregistered CAP ids:", ", ".join(missing))


if __name__ == "__main__":
    unittest.main()
