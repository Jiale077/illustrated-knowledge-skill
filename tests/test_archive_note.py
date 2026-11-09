"""Behavior checks using isolated temporary vaults; no network or image tool."""

import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "archive_note.py"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8A"
    "AwMCAO+/y9sAAAAASUVORK5CYII="
)
DRAFT = """---
title: 路由学习
type: knowledge
tags: [学习]
created: 2026-01-01
status: draft
---
# 路由学习

<!-- figure:01 -->
"""


class ArchiveNoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vault = self.root / "Vault"
        self.vault.mkdir()
        self.work = self.root / "work"
        self.work.mkdir()
        self.note = self.work / "draft.md"
        self.note.write_text(DRAFT, encoding="utf-8")
        (self.work / "figure.png").write_bytes(PNG)
        (self.work / "prompt.md").write_text("解释路由的提示词", encoding="utf-8")
        (self.work / "sources.md").write_text("资料底稿", encoding="utf-8")
        self.manifest = self.work / "images.json"
        self.images = [{"id": "01", "path": "figure.png", "prompt": "prompt.md",
                        "caption": "图 1：观察路由。"}]
        self.write_manifest()

    def write_manifest(self):
        self.manifest.write_text(json.dumps(self.images), encoding="utf-8")

    def run_archive(self, *extra, images=True, vault=True):
        command = [sys.executable, str(SCRIPT), "--note", str(self.note),
                   "--area", "Learning"]
        if vault:
            command += ["--vault", str(self.vault)]
        if images:
            command += ["--images", str(self.manifest)]
        result = subprocess.run(command + list(extra), cwd=self.work,
                                capture_output=True, text=True, encoding="utf-8")
        return result

    def success(self, *extra, **kwargs):
        result = self.run_archive(*extra, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_dry_run_does_not_create_files(self):
        plan = self.success("--dry-run")
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["images_count"], 1)
        self.assertEqual(list(self.vault.iterdir()), [])

    def test_archive_copies_assets_prompts_records_and_embeds(self):
        plan = self.success("--record", str(self.work / "sources.md"))
        note = Path(plan["note_path"]).read_text(encoding="utf-8")
        self.assertNotIn("<!-- figure:", note)
        self.assertIn("![[Attachments/illustrated-knowledge/", note)
        self.assertIn("图 1：观察路由。", note)
        self.assertEqual(Path(plan["image_paths"][0]).read_bytes(), PNG)
        assets = Path(plan["image_dir"])
        self.assertEqual((assets / "prompts/01.md").read_text(encoding="utf-8"),
                         "解释路由的提示词")
        self.assertEqual(Path(plan["record_paths"][0]).read_text(encoding="utf-8"),
                         "资料底稿")

    def test_repeated_archive_preserves_original_note(self):
        first = self.success()
        original = Path(first["note_path"]).read_bytes()
        second = self.success()
        self.assertEqual(Path(first["note_path"]).read_bytes(), original)
        self.assertTrue(second["note_path"].endswith("draft-v2.md"))
        self.assertNotEqual(first["image_dir"], second["image_dir"])

    def test_output_paths_cannot_leave_vault(self):
        for option in ("--area", "--image-root"):
            with self.subTest(option=option):
                result = self.run_archive(option, "../outside")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("leaves the vault", result.stderr)
                self.assertEqual(list(self.vault.iterdir()), [])

    def test_symlink_output_cannot_leave_vault(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.vault / "linked").symlink_to(outside, target_is_directory=True)
        result = self.run_archive("--area", "linked")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("leaves the vault", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_missing_or_duplicate_figure_ids_are_rejected(self):
        self.note.write_text(DRAFT.replace("figure:01", "figure:02"), encoding="utf-8")
        result = self.run_archive()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must match exactly once", result.stderr)
        self.note.write_text(DRAFT, encoding="utf-8")
        self.images += self.images
        self.write_manifest()
        result = self.run_archive()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Duplicate image ids", result.stderr)
        self.assertEqual(list(self.vault.iterdir()), [])

    def test_vault_is_explicitly_required(self):
        result = self.run_archive(vault=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--vault", result.stderr)
        self.assertEqual(list(self.vault.iterdir()), [])

    def test_text_only_is_explicit_and_rejects_nonempty_images(self):
        self.note.write_text(DRAFT.replace("<!-- figure:01 -->", "正文"), encoding="utf-8")
        result = self.run_archive(images=False)
        self.assertNotEqual(result.returncode, 0)
        plan = self.success("--text-only", images=False)
        self.assertEqual(plan["images_count"], 0)
        self.assertIsNone(plan["image_dir"])
        result = self.run_archive("--text-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be combined", result.stderr)


if __name__ == "__main__":
    unittest.main()
