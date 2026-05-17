import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_ROOT = ROOT / "docs" / "registry"
CAP_RE = re.compile(r"CAP-[A-Z0-9-]+")


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


def existing_rel(path: str) -> bool:
    return (ROOT / path).exists()


class DocumentRegistryTests(unittest.TestCase):
    def test_index_declares_existing_shards(self) -> None:
        index = read_rel("docs/registry/registry_index.yaml")
        for shard_path in quoted_values(index, "path"):
            if shard_path.startswith(("docs/registry/", "docs/insights/", ".jikuo/")):
                self.assertTrue(existing_rel(shard_path), shard_path)

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
        allowed_statuses = {
            "extracted_from_work_order_body",
            "no_capability_refs_found",
        }

        for entry in entries:
            statuses = quoted_values(entry, "capability_extraction_status")
            self.assertEqual(len(statuses), 1, entry[:160])
            status = statuses[0]
            self.assertIn(status, allowed_statuses)
            refs = block_values(entry, "implements_capabilities")
            if status == "extracted_from_work_order_body":
                self.assertGreater(len(refs), 0, entry[:160])
            else:
                self.assertEqual(refs, [], entry[:160])

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
