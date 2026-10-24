"""Offline tests for isler.py (registry, watchdog, dashboard). Run: python3 20-sistem/kadro/testler/isler-testleri.py"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

DIZIN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("isler_t", DIZIN / "isler.py")
isler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isler)


class IslerTestleri(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)
        yama = mock.patch.object(isler, "is_klasoru", return_value=self.d)
        yama.start()
        self.addCleanup(yama.stop)
        self.addCleanup(self.t.cleanup)
        environment = mock.patch.dict(os.environ, {"HOME": str(self.d), "CODEX_HOME": str(self.d / "codex")})
        environment.start()
        self.addCleanup(environment.stop)

    def test_shared_runner_returns_persisted_row_and_uses_environment(self):
        from types import SimpleNamespace
        arguments = SimpleNamespace(gorev="fixture", arac="codex", model="m", efor="low", ajan=None,
                                    klasor=str(self.d), sure=3, hareketsiz=2,
                                    komut=[sys.executable, "-c", "import os; print(os.environ['WORKER_MARK'])"])
        with mock.patch.object(isler, "YOKLAMA_S", 0.02), mock.patch("builtins.print") as output:
            row = isler.run_worker(arguments, directory=self.d, env={**os.environ, "WORKER_MARK": "fixture"})
        output.assert_not_called()
        self.assertEqual(row, json.loads((self.d / f"{row['id']}.json").read_text()))
        self.assertEqual(row["durum"], "bitti")
        self.assertEqual((self.d / row["log"]).read_text().strip(), "fixture")

    def test_reservation_preserves_existing_record(self):
        (self.d / "k1.json").write_text('{"id":"existing"}')
        self.assertEqual(isler.reserve_record(self.d), "k2")
        self.assertEqual(json.loads((self.d / "k1.json").read_text()), {"id": "existing"})

    def calistir(self, *komut, hareketsiz=30):
        argv = ["baslat", "--gorev", "t", "--arac", "codex", "--model", "m", "--efor", "low",
                "--hareketsiz", str(hareketsiz), "--", *komut]
        with mock.patch("builtins.print"):
            isler.main(argv)
        return json.loads(sorted(self.d.glob("k*.json"))[-1].read_text())

    def test_basarili(self):
        self.assertEqual(self.calistir(sys.executable, "-c", "print('ok')")["durum"], "bitti")

    def test_bos_cikti_basarisiz(self):
        i = self.calistir(sys.executable, "-c", "pass")
        self.assertEqual((i["durum"], i["cikis"]), ("basarisiz", 0))

    def test_ret_cikis_sifir_olsa_da(self):
        i = self.calistir(sys.executable, "-c", "print('{\"event\": \"result\", \"result\": {\"status\": \"SUCCESS\", \"denied_actions\": [{\"action\": \"command\"}]}}')")
        self.assertEqual(i["durum"], "reddedildi")

    def test_limit(self):
        self.assertEqual(self.calistir(sys.executable, "-c", "import sys; print('Error: 429 rate limit'); sys.exit(1)")["durum"], "limit")

    def test_takilma_oldurulur(self):
        i = self.calistir(sys.executable, "-c", "import time; print('x', flush=True); time.sleep(60)", hareketsiz=3)
        self.assertEqual(i["durum"], "takildi")
        self.assertLess(i["bitis"] - i["baslangic"], 30)

    def test_stdin_kapali(self):
        # a worker that waits on stdin must get EOF at once, not hang (the 2026-10-23 codex incident)
        self.assertEqual(self.calistir(sys.executable, "-c", "import sys; print(len(sys.stdin.read()))")["durum"], "bitti")

    def test_olu_izleyici_durustce_gosterilir(self):
        (self.d / "k9.json").write_text(json.dumps({"id": "k9", "durum": "calisiyor", "pid": 999999, "baslangic": 1}))
        self.assertEqual(isler.isleri_oku(self.d)[0]["durum"], "basarisiz")

    def test_kod_icindeki_429_limit_sayilmaz(self):
        # a worker that writes tests about 429 must still finish as "bitti" (k1 false positive)
        i = self.calistir(sys.executable, "-c", "print('x = 1\\n' * 2500); print('def test_429_rate_limit(): pass'); print('denied_actions: []'); print('Tamamlandı: 31 test OK')")
        self.assertEqual(i["durum"], "bitti")

    def test_codex_turn_failed_limit(self):
        i = self.calistir(sys.executable, "-c", "print('{\"type\": \"turn.failed\", \"error\": {\"message\": \"usage limit reached\"}}')")
        self.assertEqual(i["durum"], "limit")

    def test_opencode_hata_satiri_cikis_sifir(self):
        i = self.calistir(sys.executable, "-c", "print('> build'); print('Error: Model unavailable: yerel/x')")
        self.assertEqual(i["durum"], "basarisiz")

    def test_kimlik_artar(self):
        (self.d / "k7.json").write_text("{}")
        self.assertEqual(isler.yeni_kimlik(self.d), "k8")


if __name__ == "__main__":
    unittest.main(verbosity=1)
