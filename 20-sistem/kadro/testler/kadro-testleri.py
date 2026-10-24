#!/usr/bin/env python3
"""Exercise the roster with isolated files and no external services."""
from __future__ import annotations

import copy
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROSTER_DIR = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("roster", ROSTER_DIR / "kadro.py")
roster = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(roster)


def quota(cli: str, mode: str = "normal", binding: str = "hafta") -> dict:
    return {"arac": cli, "baglayici": binding, "kalan_yuzde": 50,
            "kip": mode, "pencereler": {"5s": None, "hafta": None}}


def measurement(**updates) -> dict:
    row = {"gorev": "kod-duzeltme", "cli": "codex", "model": "varsayilan",
           "efor": "high", "sure_sn": 12, "basari": True, "puan": None,
           "kota_farki": 0.5, "not": "fixture"}
    return {**row, **updates}


class RosterTests(unittest.TestCase):
    def setUp(self):
        self.guards = ExitStack()
        self.addCleanup(self.guards.close)
        for target in ("subprocess.Popen", "socket.socket", "socket.create_connection",
                       "pathlib.Path.home", "os.path.expanduser"):
            self.guards.enter_context(patch(target, side_effect=AssertionError(target)))
        self.directory = tempfile.TemporaryDirectory(prefix="roster-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.config = roster.load_config(ROSTER_DIR / "kadro.json")
        self.config_path = self.root / "kadro.json"
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        self.source = self.root / "input.jsonl"
        self.quotas = [quota(cli) for cli in ("claude", "codex", "agy")]

    def write_rows(self, *rows):
        self.source.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    def add_scores(self, task_type, candidate, count, total):
        self.config["olcumler"][roster.measurement_key(task_type, candidate)] = {
            "n": count, "toplam_puan": total,
            "toplam_sure_sn": 0, "toplam_kota_farki": 0,
        }

    def test_initial_schema_and_placeholders(self):
        self.assertEqual(set(self.config["is_turu"]), set(roster.TASK_TYPES))
        self.assertTrue(self.config["inceleme_saglayici_farkli"])
        for group in ("is_turu", "yedek"):
            for candidates in self.config[group].values():
                self.assertTrue(all(item["model"] == "varsayilan" for item in candidates))

    def test_full_claude_quota_never_receives_any_heavy_task(self):
        quotas = [quota("claude", "dolu"), quota("codex"), quota("agy")]
        for task_type in roster.TASK_TYPES[:-1]:
            with self.subTest(task_type=task_type, situation="alternatives available"):
                result = roster.select(task_type, self.config, quotas, "openai")
                self.assertIsNotNone(result["aday"])
                self.assertNotEqual(result["aday"]["cli"], "claude")
            with self.subTest(task_type=task_type, situation="only Claude remains"):
                blocked = [quota(cli, "dolu") for cli in ("claude", "codex", "agy")]
                result = roster.select(task_type, self.config, blocked, "openai")
                self.assertIsNone(result["aday"])
                self.assertTrue(any(entry["aday"]["cli"] == "claude"
                                    and entry["kota"]["kip"] == "dolu"
                                    for entry in result["elenenler"]))

    def test_empty_measurements_follow_order_within_quota_mode(self):
        result = roster.select("kod-duzeltme", self.config, self.quotas)
        self.assertEqual(result["aday"], self.config["is_turu"]["kod-duzeltme"][0])
        self.assertEqual(result["olcum"]["n"], 0)
        self.assertEqual(result["olcum"]["puan"], 0.75)
        self.assertIsNone(result["olcum"]["ortalama"])
        self.assertEqual(result["kota"]["baglayici"], "hafta")

    def test_review_rejects_writer_provider(self):
        result = roster.select("inceleme", self.config, self.quotas, "google")
        self.assertEqual(result["aday"]["cli"], "codex")
        self.assertEqual(result["saglayici"], "openai")
        self.assertIn("aynı sağlayıcı", result["elenenler"][0]["gerekce"])

    def test_agy_claude_is_anthropic_but_uses_agy_quota(self):
        self.config["is_turu"]["inceleme"][0]["model"] = "claude-placeholder"
        result = roster.select("inceleme", self.config, self.quotas, "anthropic")
        self.assertEqual(result["aday"]["cli"], "codex")
        allowed = roster.select("inceleme", self.config, self.quotas, "openai")
        self.assertEqual(allowed["saglayici"], "anthropic")
        self.assertEqual(allowed["kota"]["arac"], "agy")
        quotas = [quota("agy", "dolu"), quota("claude"), quota("codex", "dolu")]
        fallback = roster.select("inceleme", self.config, quotas, "openai")
        self.assertEqual(fallback["aday"]["cli"], "claude")
        self.assertTrue(fallback["yedek"])

    def test_review_requires_writer_even_for_fallback(self):
        result = roster.select("inceleme", self.config, self.quotas)
        self.assertEqual(result["durum"], "yazan_saglayici_gerekli")
        self.assertIsNone(result["aday"])
        quotas = [quota("claude"), quota("codex", "dolu"), quota("agy", "dolu")]
        result = roster.select("inceleme", self.config, quotas, "anthropic")
        self.assertIsNone(result["aday"])

    def test_thrifty_quota_only_for_hard_tasks_and_review(self):
        quotas = [quota(cli, "idareli") for cli in ("claude", "codex", "agy")]
        for task_type in roster.TASK_TYPES:
            with self.subTest(task_type=task_type):
                result = roster.select(task_type, self.config, quotas, "openai")
                self.assertEqual(result["aday"] is not None,
                                 task_type in self.config["zor_isler"])

    def test_unknown_missing_and_unsupported_quota_never_auto_select(self):
        for mode in ("bilinmiyor", "n/a", "unexpected"):
            with self.subTest(mode=mode):
                result = roster.select("kod-duzeltme", self.config,
                                       [quota(cli, mode) for cli in ("claude", "codex", "agy")])
                self.assertEqual(result["durum"], "uygun_aday_yok")
                self.assertEqual(len(result["bilinmeyenler"]), 3)
                self.assertIn("bilinmeyen", result["gerekce"])
        result = roster.select("basit", self.config, [])
        self.assertIsNone(result["aday"])
        self.assertEqual(len(result["bilinmeyenler"]), 3)

    def test_healthy_fallback_can_replace_unknown_primary(self):
        result = roster.select("kod-duzeltme", self.config, [quota("claude")])
        self.assertEqual(result["aday"]["cli"], "claude")
        self.assertTrue(result["yedek"])

    def test_quota_mode_precedes_score_and_primary_precedes_fallback(self):
        result = roster.select("kod-duzeltme", self.config,
                               [quota("codex"), quota("agy", "bol"), quota("claude", "bol")])
        self.assertEqual(result["aday"]["cli"], "agy")
        result = roster.select("kod-duzeltme", self.config,
                               [quota("codex"), quota("agy", "dolu"), quota("claude", "bol")])
        self.assertEqual(result["aday"]["cli"], "codex")

    def test_bayesian_blend_and_observations_change_selection(self):
        first, second = self.config["is_turu"]["kod-duzeltme"]
        self.add_scores("kod-duzeltme", first, 5, 0)
        evidence = roster.score_candidate("kod-duzeltme", first, 0, self.config)
        self.assertAlmostEqual(evidence["a"], 0.5)
        self.assertAlmostEqual(evidence["puan"], 0.375)
        result = roster.select("kod-duzeltme", self.config, self.quotas)
        self.assertEqual(result["aday"], second)
        self.add_scores("kod-duzeltme", first, 1, 1)
        evidence = roster.score_candidate("kod-duzeltme", first, 0, self.config)
        self.assertAlmostEqual(evidence["a"], 1 / 6)
        self.assertAlmostEqual(evidence["puan"], 5 / 6 * 0.75 + 1 / 6)

    def test_measurement_identity_separates_task_cli_model_effort(self):
        candidate = self.config["is_turu"]["kod-duzeltme"][0]
        self.add_scores("kod-duzeltme", candidate, 5, 0)
        for changed in ({**candidate, "efor": "medium"},
                        {**candidate, "model": "another|model"},
                        {**candidate, "cli": "agy"}):
            self.assertEqual(roster.score_candidate("kod-duzeltme", changed, 0,
                                                    self.config)["n"], 0)
        self.assertEqual(roster.score_candidate("arastirma", candidate, 0, self.config)["n"], 0)

    def test_learning_is_idempotent_and_normalizes_numbers(self):
        row = measurement()
        self.write_rows(row, row, {**row, "sure_sn": 12.0, "basari": 1})
        result = roster.learn(self.source, self.config_path)
        self.assertEqual(result, {"eklenen": 1, "tekrar": 2})
        original = self.config_path.read_bytes()
        self.assertEqual(roster.learn(self.source, self.config_path), {"eklenen": 0, "tekrar": 3})
        self.assertEqual(original, self.config_path.read_bytes())
        config = roster.load_config(self.config_path)
        record = config["olcumler"][roster.measurement_key(row["gorev"], row)]
        self.assertEqual(record, {"n": 1, "toplam_puan": 1,
                                  "toplam_sure_sn": 12, "toplam_kota_farki": 0.5})

    def test_explicit_ids_distinguish_identical_experiments(self):
        self.write_rows(measurement(id="trial-1"), measurement(id="trial-2"))
        self.assertEqual(roster.learn(self.source, self.config_path)["eklenen"], 2)
        self.assertEqual(roster.learn(self.source, self.config_path)["tekrar"], 2)

    def test_duplicate_id_with_different_content_is_transactional(self):
        self.write_rows(measurement(id="trial"), measurement(id="trial", puan=3))
        original = self.config_path.read_bytes()
        with self.assertRaises(roster.InputError):
            roster.learn(self.source, self.config_path)
        self.assertEqual(original, self.config_path.read_bytes())
        self.assertFalse(self.config_path.with_name("kadro-kilit.tmp").exists())

    def test_rating_and_success_are_normalized_and_averaged(self):
        self.write_rows(measurement(id="rating-only", basari=None, puan=4),
                        measurement(id="mixed", basari=0.5, puan=1, kota_farki=-2))
        roster.learn(self.source, self.config_path)
        config = roster.load_config(self.config_path)
        record = next(iter(config["olcumler"].values()))
        self.assertEqual(record["n"], 2)
        self.assertAlmostEqual(record["toplam_puan"], 0.8 + (0.5 + 0.2) / 2)
        self.assertAlmostEqual(record["toplam_kota_farki"], -1.5)

    def test_invalid_measurements_preserve_original_file(self):
        invalid = [None, [], {}, measurement(gorev="unknown"), measurement(cli="unknown"),
                   measurement(model=""), measurement(efor=[]), measurement(sure_sn=-1),
                   measurement(sure_sn=True), measurement(basari=2), measurement(puan=6),
                   measurement(basari=None, puan=None), measurement(puan=True),
                   measurement(kota_farki="bad"), measurement(not_=5),
                   measurement(**{"not": []}), measurement(id=""),
                   measurement(sure_sn=float("inf")), measurement(puan=float("nan"))]
        original = self.config_path.read_bytes()
        for row in invalid:
            with self.subTest(row_type=type(row).__name__, row=row):
                self.write_rows(measurement(id="good"), row)
                with self.assertRaises(roster.InputError):
                    roster.learn(self.source, self.config_path)
                self.assertEqual(original, self.config_path.read_bytes())

    def test_empty_broken_and_duplicate_field_json_are_rejected(self):
        for content in ("", "\n  \n", "{broken", '{"gorev":"basit","gorev":"inceleme"}'):
            with self.subTest(content=content):
                original = self.config_path.read_bytes()
                self.source.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    roster.learn(self.source, self.config_path)
                self.assertEqual(original, self.config_path.read_bytes())

    def test_invalid_config_and_quota_fail_without_selection(self):
        for change in ({"inceleme_saglayici_farkli": False}, {"surum": True},
                       {"is_turu": []}, {"olcumler": {"bad-key": {}}}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    roster.select("kod-duzeltme", {**self.config, **change}, self.quotas)
        for rows in (None, [None], [quota("codex"), quota("codex")],
                     [quota("codex", binding="openai")],
                     [{**quota("codex"), "kalan_yuzde": float("nan")}],
                     [{**quota("codex"), "pencereler": []}]):
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    roster.select("kod-duzeltme", self.config, rows)

    def test_failed_atomic_replace_preserves_file_and_cleans_temporary_files(self):
        self.write_rows(measurement())
        original = self.config_path.read_bytes()
        with patch.object(roster.os, "replace", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                roster.learn(self.source, self.config_path)
        self.assertEqual(original, self.config_path.read_bytes())
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_existing_lock_prevents_another_writer(self):
        self.write_rows(measurement())
        lock = self.config_path.with_name("kadro-kilit.tmp")
        lock.write_text("fixture", encoding="utf-8")
        original = self.config_path.read_bytes()
        with self.assertRaises(roster.InputError):
            roster.learn(self.source, self.config_path)
        self.assertEqual(lock.read_text(encoding="utf-8"), "fixture")
        self.assertEqual(original, self.config_path.read_bytes())

    def test_quota_adapter_reads_only_fixture_cache_and_disables_cli_refresh(self):
        reader_dir = self.root / "20-sistem" / "nabiz"
        reader_dir.mkdir(parents=True)
        shutil.copyfile(ROSTER_DIR.parent / "nabiz" / "kota.py", reader_dir / "kota.py")
        fixture_sessions = self.root / "codex-fixture"
        fixture_sessions.mkdir()
        with patch.dict(os.environ, {"CODEX_HOME": str(fixture_sessions)}), \
                patch("shutil.which", return_value="fake-agy"):
            rows = roster.load_quotas(self.root)
            indexed = roster.quota_index(rows)
            self.assertEqual(indexed["agy"]["kip"], "bilinmiyor")
            self.assertEqual(indexed["codex"]["kip"], "bilinmiyor")
            cache = self.root / "20-sistem" / "durum" / "fixture-host"
            cache.mkdir(parents=True)
            from datetime import datetime, timezone
            now = time.time()
            reset = datetime.fromtimestamp(now + 600, timezone.utc).isoformat()
            payload = {"zaman": now, "veri": {"groups": [{"buckets": [
                {"remaining_fraction": 0.8, "window": "5h", "reset_time": reset},
            ]}]}}
            (cache / "kota-agy.json").write_text(json.dumps(payload), encoding="utf-8")
            snapshot = {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
            with patch("socket.gethostname", return_value="fixture-host"):
                rows = roster.load_quotas(self.root)
            self.assertEqual(roster.quota_index(rows)["agy"]["kip"], "bol")
            self.assertEqual(snapshot, {str(path): path.read_bytes()
                                        for path in self.root.rglob("*") if path.is_file()})

    def invoke(self, args, quotas=None):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(roster, "load_config", return_value=copy.deepcopy(self.config)), \
                patch.object(roster, "load_quotas", return_value=self.quotas if quotas is None else quotas), \
                redirect_stdout(output), redirect_stderr(errors):
            status = roster.main(args)
        return status, output.getvalue(), errors.getvalue()

    def test_cli_json_selection_and_no_candidate_exit_codes(self):
        status, output, _ = self.invoke(["secim", "kod-duzeltme", "--json"])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output)["aday"]["cli"], "codex")
        status, output, _ = self.invoke(["secim", "kod-duzeltme", "--json"], [])
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output)["durum"], "uygun_aday_yok")
        status, output, _ = self.invoke(["secim", "inceleme", "--json"])
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output)["durum"], "yazan_saglayici_gerekli")

    def test_show_reports_all_tasks_and_measurement_quota_reasons(self):
        status, output, _ = self.invoke(["goster", "--yazan-saglayici", "openai"])
        self.assertEqual(status, 0)
        for task_type in roster.TASK_TYPES:
            self.assertIn(task_type + ":", output)
        self.assertIn("n=0", output)
        self.assertIn("önsel=", output)
        self.assertIn("bağlayıcı=hafta", output)
        status, output, _ = self.invoke(["goster", "--json"])
        self.assertEqual(len(json.loads(output)), 6)

    def test_cli_learning_and_input_error_status(self):
        self.write_rows(measurement())
        with patch.object(roster, "CONFIG_PATH", self.config_path), \
                patch.object(roster, "learn", wraps=lambda path: roster_learn(path, self.config_path)):
            status, output, _ = self.invoke(["ogren", str(self.source)])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output), {"eklenen": 1, "tekrar": 0})
        with patch.object(roster, "load_quotas", side_effect=roster.InputError("fixture error")), \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(roster.main(["secim", "basit", "--json"]), 2)
        self.assertEqual(json.loads(output.getvalue())["durum"], "hata")


roster_learn = roster.learn

if __name__ == "__main__":
    unittest.main(verbosity=2)
