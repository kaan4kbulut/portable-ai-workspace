"""Exercise offline evaluators and the runner in a temporary repository copy."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from uuid import UUID
from datetime import datetime


SOURCE = Path(__file__).resolve().parents[1]
TASKS = ("kod-duzeltme", "inceleme", "turkce-belge", "arastirma", "mekanik-tasima")
FIELDS = {"id", "tarih", "gorev", "cli", "model", "efor", "sure_sn", "basari", "puan", "kota_farki", "not"}
BOOTSTRAP = """
import runpy
import sys

def audit(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('Network access is forbidden during tests')

sys.addaudithook(audit)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.base = self.root / "repo" / "20-sistem" / "kadro" / "olcum"
        shutil.copytree(SOURCE, self.base)
        self.tasks = self.base.parent / "gorevler"
        shutil.copytree(SOURCE.parent / "gorevler", self.tasks)
        self.home = self.root / "home"
        self.home.mkdir()
        self.environment = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                                XDG_CONFIG_HOME=str(self.home), XDG_CACHE_HOME=str(self.home))
        self.runner = self.base / "kosucu.py"

    def run_script(self, script, *arguments, expected=0):
        process = subprocess.run(
            [sys.executable, "-I", "-B", "-c", BOOTSTRAP, str(script), *map(str, arguments)],
            cwd=self.root, env=self.environment, capture_output=True, text=True, timeout=20,
            check=False,
        )
        self.assertEqual(process.returncode, expected, process.stdout + process.stderr)
        return process

    def copy_fixture(self, task, solution=False):
        folder = self.root / (task + ("-good" if solution else "-bad"))
        manifest = self.tasks / task / ("cozum.json" if solution else "girdi.json")
        folder.mkdir()
        for name, content in json.loads(manifest.read_text(encoding="utf-8")).items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return folder

    def evaluate(self, task, folder):
        process = self.run_script(self.tasks / task / "degerlendir.py", folder)
        outcome = json.loads(process.stdout)
        self.assertEqual(set(outcome), {"basari", "puan", "not"})
        self.assertIs(type(outcome["basari"]), bool)
        self.assertTrue(0 <= outcome["puan"] <= 1)
        self.assertIsInstance(outcome["not"], str)
        return outcome

    def measure(self, task, folder, *extra, expected=0):
        return self.run_script(self.runner, "degerlendir", task, folder,
                               "--cli", "codex", "--model", "fixture-model", "--efor", "medium",
                               "--sure", "1.25", *extra, expected=expected)

    def test_all_reference_solutions_succeed(self):
        for task in TASKS:
            with self.subTest(task=task):
                outcome = self.evaluate(task, self.copy_fixture(task, solution=True))
                self.assertTrue(outcome["basari"], outcome)
                self.assertEqual(outcome["puan"], 1)

    def test_all_unmodified_inputs_fail(self):
        for task in TASKS:
            with self.subTest(task=task):
                outcome = self.evaluate(task, self.copy_fixture(task))
                self.assertFalse(outcome["basari"], outcome)
                self.assertEqual(outcome["puan"], 0)

    def test_code_test_hash_is_enforced(self):
        folder = self.copy_fixture("kod-duzeltme", solution=True)
        path = folder / "testler.py"
        path.write_text(path.read_text() + "\n# Altered test\n", encoding="utf-8")
        outcome = self.evaluate("kod-duzeltme", folder)
        self.assertFalse(outcome["basari"])
        self.assertIn("SHA-256", outcome["not"])

    def test_review_partial_duplicate_and_wrong_line(self):
        folder = self.copy_fixture("inceleme", solution=True)
        path = folder / "bulgular.json"
        finding = json.loads(path.read_text())["bulgular"][0]
        path.write_text(json.dumps({"bulgular": [finding, finding]}))
        self.assertAlmostEqual(self.evaluate("inceleme", folder)["puan"], 1 / 3)
        finding["satir"] = 8
        path.write_text(json.dumps({"bulgular": [finding]}))
        self.assertEqual(self.evaluate("inceleme", folder)["puan"], 0)

    def test_document_missing_empty_or_fenced_sections_fail(self):
        folder = self.copy_fixture("turkce-belge", solution=True)
        path = folder / "README.md"
        good = path.read_text()
        for text in (good.replace("## Girmez", "## Kapsam"),
                     good.replace("Kimlik bilgileri, görseller ve indirilen arşivler.", ""),
                     "```\n" + good + "```\n", good.replace("# Not düzenleyici", "# Başka")):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                self.assertFalse(self.evaluate("turkce-belge", folder)["basari"])

    def test_research_urls_citations_and_length(self):
        folder = self.copy_fixture("arastirma", solution=True)
        path = folder / "rapor.md"
        good = path.read_text()
        for text in (good.replace("https://", "file://"), good.replace("[2]", "[1]"),
                     good.replace("[1].", "[3]."),
                     good.replace("## Özet\n", "## Özet\n" + "sözcük " * 181)):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                self.assertFalse(self.evaluate("arastirma", folder)["basari"])

    def test_move_checks_config_links_and_content(self):
        folder = self.copy_fixture("mekanik-tasima", solution=True)
        changes = {"ayar.json": '{"help":"eski/kilavuz.md"}',
                   "README.md": "[Kılavuz](eski/kilavuz.md)\n",
                   "belgeler/kilavuz.md": "Değişmiş içerik\n"}
        for name, content in changes.items():
            path = folder / name
            original = path.read_bytes()
            path.write_text(content, encoding="utf-8")
            self.assertFalse(self.evaluate("mekanik-tasima", folder)["basari"])
            path.write_bytes(original)

    def test_missing_and_malformed_outputs_fail_as_json(self):
        for task, name in (("inceleme", "bulgular.json"), ("mekanik-tasima", "ayar.json")):
            with self.subTest(task=task):
                folder = self.copy_fixture(task, solution=True)
                (folder / name).write_text("{not json", encoding="utf-8")
                self.assertFalse(self.evaluate(task, folder)["basari"])
        for task in TASKS:
            with self.subTest(missing=task):
                self.assertFalse(self.evaluate(task, self.root / "missing")["basari"])

    def test_prepare_copies_only_input_and_does_not_overwrite(self):
        for task in TASKS:
            with self.subTest(task=task):
                target = self.root / (task + "-prepared")
                self.run_script(self.runner, "hazirla", task, target)
                source = json.loads((self.tasks / task / "girdi.json").read_text(encoding="utf-8"))
                actual = {p.relative_to(target).as_posix(): p.read_text(encoding="utf-8")
                          for p in target.rglob("*") if p.is_file()}
                self.assertEqual(source, actual)
                self.run_script(self.runner, "hazirla", task, target, expected=2)

    def test_command_exact_arguments_and_no_execution(self):
        prompt = (self.tasks / "inceleme" / "istem.md").read_text()
        folder = "work with spaces"
        expected = {
            "codex": ["codex", "exec", "-C", folder, "-s", "workspace-write", "-m", "model",
                      "-c", "model_reasoning_effort=high", prompt],
            "agy": ["agy", "-p", prompt, "--model", "model", "--effort", "high", "--output-format",
                    "stream-json", "--sandbox", "--mode", "accept-edits"],
            "opencode": ["opencode", "run", "-m", "model", prompt],
        }
        for cli, command in expected.items():
            with self.subTest(cli=cli):
                process = self.run_script(self.runner, "komut", "inceleme", "--cli", cli,
                                          "--model", "model", "--efor", "high", folder)
                self.assertEqual(json.loads(process.stdout), command)
        self.assertFalse((self.base.parent / "olcumler").exists())

    def test_jsonl_append_schema_and_failed_measurement(self):
        folder = self.copy_fixture("kod-duzeltme", solution=True)
        first = json.loads(self.measure("kod-duzeltme", folder).stdout)
        bad = self.copy_fixture("kod-duzeltme")
        second = json.loads(self.measure("kod-duzeltme", bad).stdout)
        paths = list((self.base.parent / "olcumler").glob("*.jsonl"))
        self.assertEqual(len(paths), 1)
        records = [json.loads(line) for line in paths[0].read_text().splitlines()]
        self.assertEqual(records, [first, second])
        self.assertNotEqual(first["id"], second["id"])
        for record in records:
            self.assertEqual(set(record), FIELDS)
            UUID(record["id"])
            self.assertIsNotNone(datetime.fromisoformat(record["tarih"]).tzinfo)
            self.assertEqual(record["tarih"][:10], paths[0].stem)
            self.assertEqual(record["sure_sn"], 1.25)
            self.assertIsNone(record["kota_farki"])
        self.assertTrue(first["basari"])
        self.assertFalse(second["basari"])
        self.assertEqual(second["puan"], 0)
        self.assertEqual(list(self.home.iterdir()), [])

    def quota(self, name, used, reset=100):
        path = self.root / name
        path.write_text(json.dumps([{"arac": "codex", "pencereler": {
            "5s": {"kullanilan": used, "sifirlanma": reset}, "hafta": None}}]))
        return path

    def test_quota_difference_and_reset(self):
        folder = self.copy_fixture("arastirma", solution=True)
        before = self.quota("before.json", 0.2)
        after = self.quota("after.json", 0.3)
        record = json.loads(self.measure("arastirma", folder, "--kota-oncesi", before,
                                         "--kota-sonrasi", after).stdout)
        self.assertEqual(record["kota_farki"], {"5s": 0.1, "hafta": None})
        for used, reset in ((0.1, 200), (0.1, 100)):
            after = self.quota("after.json", used, reset)
            record = json.loads(self.measure("arastirma", folder, "--kota-oncesi", before,
                                             "--kota-sonrasi", after).stdout)
            self.assertEqual(record["kota_farki"], {"5s": None, "hafta": None})

    def test_invalid_measurements_do_not_write_logs(self):
        folder = self.copy_fixture("arastirma", solution=True)
        before = self.quota("before.json", 0.2)
        for value in ("nan", "inf", "-1"):
            self.measure("arastirma", folder, "--sure", value, expected=2)
        self.measure("arastirma", folder, "--kota-oncesi", before, expected=2)
        before.write_text("{}")
        self.measure("arastirma", folder, "--kota-oncesi", before,
                     "--kota-sonrasi", before, expected=2)
        self.assertFalse((self.base.parent / "olcumler").exists())

    def test_fixtures_have_readmes_no_symlinks_and_no_modified_tests(self):
        for root in (self.base, self.tasks):
            for path in root.rglob("*"):
                self.assertFalse(path.is_symlink())
                if path.is_dir():
                    self.assertTrue((path / "README.md").is_file(), str(path))
                self.assertLessEqual(len(path.relative_to(self.root / "repo").parts)
                                     - int(path.is_file()), 4)
        task = self.tasks / "kod-duzeltme"
        expected = "d10eb2173e4e16c210315e9cfa8506978a6b6bd950050f0a97a693fe6988c752"
        for name in ("girdi.json", "cozum.json"):
            content = json.loads((task / name).read_text(encoding="utf-8"))["testler.py"]
            self.assertEqual(hashlib.sha256(content.encode("utf-8")).hexdigest(), expected)
        for task in TASKS:
            folder = self.tasks / task
            self.assertTrue(all(path.is_file() for path in folder.iterdir()))
            self.assertLessEqual({path.name for path in folder.iterdir()},
                                 {"README.md", "istem.md", "degerlendir.py", "rubrik.md",
                                  "girdi.json", "cozum.json"})
        self.assertFalse((self.base / "gorevler").exists())

    def test_invalid_manifests_do_not_create_targets(self):
        manifest = self.tasks / "inceleme" / "girdi.json"
        invalid = ([], {"../escaped": "x"}, {"nested/../../escaped": "x"},
                   {"/escaped": "x"}, {"C:/escaped": "x"}, {"C:escaped": "x"},
                   {"nested\\escaped": "x"}, {"": "x"}, {"./file": "x"},
                   {"nested//file": "x"}, {"file/": "x"}, {"file": 1},
                   {"file": "x", "file/child": "y"})
        target = self.root / "prepared"
        for data in invalid:
            with self.subTest(data=data):
                manifest.write_text(json.dumps(data), encoding="utf-8")
                self.run_script(self.runner, "hazirla", "inceleme", target, expected=2)
                self.assertFalse(target.exists())
                self.assertFalse((self.root / "escaped").exists())
        manifest.write_text("{broken", encoding="utf-8")
        self.run_script(self.runner, "hazirla", "inceleme", target, expected=2)
        self.assertFalse(target.exists())



if __name__ == "__main__":
    unittest.main(verbosity=2)
