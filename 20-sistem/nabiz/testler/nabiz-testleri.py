#!/usr/bin/env python3
"""Offline tests for kota.py, durum-satiri.py, takip.py. Run: python3 20-sistem/nabiz/testler/nabiz-testleri.py

Everything uses temp dirs; network and subprocess are mocked; the real home dir is never touched.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

NABIZ = Path(__file__).resolve().parent.parent


def yukle(ad: str, dosya: str):
    spec = importlib.util.spec_from_file_location(ad, NABIZ / dosya)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


kota = yukle("kota_t", "kota.py")
durum = yukle("durum_t", "durum-satiri.py")
takip = yukle("takip_t", "takip.py")
SIMDI = 1_800_000_000.0


def sahte_kok(tmp: Path) -> Path:
    (tmp / "00-cekirdek").mkdir(parents=True)
    (tmp / "00-cekirdek" / "ANAYASA.md").write_text("x")
    (tmp / "90-gelen-kutusu").mkdir()
    (tmp / "90-gelen-kutusu" / "README.md").write_text("x")
    return tmp


class KotaTestleri(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.kok = sahte_kok(Path(self._t.name))

    def tearDown(self):
        self._t.cleanup()

    def test_kip_bol_normal_idareli_dolu(self):
        h = {"kullanilan": 0.1, "sifirlanma": SIMDI + 6 * 86400}
        f = lambda k, s=3 * 3600: {"kullanilan": k, "sifirlanma": SIMDI + s}
        self.assertEqual(kota.kip_hesapla(f(0.1), h, SIMDI, SIMDI), "bol")
        self.assertEqual(kota.kip_hesapla(f(0.6), h, SIMDI, SIMDI), "normal")
        self.assertEqual(kota.kip_hesapla(f(0.85), h, SIMDI, SIMDI), "idareli")
        self.assertEqual(kota.kip_hesapla(f(0.99), h, SIMDI, SIMDI), "dolu")
        self.assertEqual(kota.kip_hesapla(f(0.5), h, None, SIMDI), "bilinmiyor")
        self.assertEqual(kota.kip_hesapla(f(0.5), h, SIMDI - 7 * 3600, SIMDI), "bilinmiyor")

    def test_pencere_bitmek_uzere_bol(self):
        f = {"kullanilan": 0.8, "sifirlanma": SIMDI + 900}
        self.assertEqual(kota.kip_hesapla(f, None, SIMDI, SIMDI), "bol")

    def test_sifirlanmis_pencere_sifirdan(self):
        f = {"kullanilan": 0.99, "sifirlanma": SIMDI - 10}
        self.assertEqual(kota.kalan_yuzde(f, None, SIMDI), 100)

    def test_claude_onbellek_yaz_oku(self):
        girdi = {"rate_limits": {"five_hour": {"used_percentage": 23.5, "resets_at": SIMDI + 3600},
                                 "seven_day": {"used_percentage": 41.2, "resets_at": SIMDI + 86400}}}
        self.assertTrue(kota.claude_onbellege_yaz(self.kok, girdi, SIMDI, "h"))
        s = kota.claude_oku(self.kok, SIMDI + 10, "h")
        self.assertEqual(s["kalan_yuzde"], 59)  # 100-41
        self.assertNotEqual(s["kip"], "bilinmiyor")

    def test_claude_rate_limits_yoksa_eski_korunur(self):
        self.assertFalse(kota.claude_onbellege_yaz(self.kok, {"model": {}}, SIMDI, "h"))
        self.assertEqual(kota.claude_oku(self.kok, SIMDI, "h")["kip"], "bilinmiyor")

    def test_codex_rollout(self):
        gun = self.kok / "sessions" / "2026" / "10" / "23"
        gun.mkdir(parents=True)
        olay = {"payload": {"rate_limits": {
            "primary": {"used_percent": 30, "window_minutes": 300, "resets_at": SIMDI + 3600},
            "secondary": {"used_percent": 10, "window_minutes": 10080, "resets_at": SIMDI + 86400 * 3}}}}
        (gun / "rollout-a.jsonl").write_text(json.dumps({"x": 1}) + "\n" + json.dumps(olay) + "\n")
        s = kota.codex_oku(time.time(), self.kok / "sessions")
        self.assertEqual(s["kalan_yuzde"], 70)
        self.assertIsNotNone(s["pencereler"]["hafta"])

    def test_codex_olay_zamani_kullanilir(self):
        gun = self.kok / "sessions" / "2026" / "10" / "23"
        gun.mkdir(parents=True)
        t0 = datetime(2026, 10, 23, 10, 0, tzinfo=timezone.utc).timestamp()
        olay = {"timestamp": "2026-10-23T10:00:00Z", "payload": {"rate_limits": {
            "primary": {"used_percent": 30, "window_minutes": 300, "resets_in_seconds": 3600}}}}
        (gun / "rollout-a.jsonl").write_text(json.dumps(olay) + "\n")  # mtime = now, olay zamanından çok sonra
        s = kota.codex_oku(t0 + 60, self.kok / "sessions")
        self.assertAlmostEqual(s["pencereler"]["5s"]["sifirlanma"], t0 + 3600, delta=1)

    def test_codex_veri_yok(self):
        s = kota.codex_oku(SIMDI, self.kok / "yok")
        self.assertEqual((s["kip"], s["kalan_yuzde"]), ("bilinmiyor", None))

    def test_agy_taklit(self):
        veri = {"command": {"data": {"groups": [{"name": "Gemini", "buckets": [
            {"window": "5h", "remaining_fraction": 0.4, "reset_time": "2027-01-01T00:00:00Z"}]}]}}}
        sim = datetime(2026, 12, 31, 22, tzinfo=timezone.utc).timestamp()
        with mock.patch.object(kota.shutil, "which", return_value="/x/agy"):
            s = kota.agy_oku(self.kok, sim, "h", calistir=lambda y: veri)
        self.assertEqual(s["kalan_yuzde"], 40)
        # ikinci çağrı önbellekten gelir, çalıştırıcı çağrılmaz
        s2 = kota.agy_oku(self.kok, sim + 5, "h", calistir=lambda y: self.fail("önbellek kullanılmalı"))
        self.assertEqual(s2["kalan_yuzde"], 40)

    def test_agy_kurulu_degil(self):
        with mock.patch.object(kota.shutil, "which", return_value=None):
            self.assertEqual(kota.agy_oku(self.kok, SIMDI, "h")["kip"], "bilinmiyor")

    def test_hepsi_opencode_na(self):
        with mock.patch.object(kota, "codex_oturum_klasoru", return_value=self.kok / "yok"):
            r = kota.hepsi(self.kok, SIMDI, "h", agy=False)
        self.assertEqual([x["arac"] for x in r], ["claude", "codex", "opencode"])
        self.assertEqual(r[-1]["kip"], "n/a")


class DurumSatiriTestleri(unittest.TestCase):
    def test_satir_ve_hiz(self):
        with tempfile.TemporaryDirectory() as t:
            kok = sahte_kok(Path(t) / "atolye")  # klasör adı = ad
            d = kok / "20-sistem" / "durum" / "mk"
            d.mkdir(parents=True)
            (d / "son-denetim.txt").write_text("[HATA] a\n[UYARI] b\n[UYARI] c\n[OK] d\n")
            (kok / "90-gelen-kutusu" / "not.md").write_text("x")
            girdi = {"rate_limits": {"five_hour": {"used_percentage": 20, "resets_at": time.time() + 3600}}}
            with mock.patch.object(durum, "git_degisiklik", return_value="3"):
                bas = time.perf_counter()
                satir = durum.satir_uret(kok, kota, girdi, time.time(), "mk", kok / "yok")
                gecen = time.perf_counter() - bas
            self.assertEqual(satir.split(" · ")[:5], ["atolye", "mk", "git ±3", "gelen 1", "denetim 1/2"])
            self.assertIn("claude 80%", satir)
            self.assertIn("codex ?", satir)
            self.assertLess(gecen, 0.2)

    def test_kimlik_json_adi(self):
        with tempfile.TemporaryDirectory() as t:
            kok = sahte_kok(Path(t))
            (kok / "00-cekirdek" / "kimlik.json").write_text(json.dumps({"ad": "Kaan"}))
            self.assertEqual(durum.ad_bul(kok), "Kaan")

    def test_bos_girdi_ve_denetim_yok(self):
        with tempfile.TemporaryDirectory() as t:
            kok = sahte_kok(Path(t))
            with mock.patch.object(durum, "git_degisiklik", return_value="0"):
                satir = durum.satir_uret(kok, kota, {}, SIMDI, "mk", kok / "yok")
            self.assertIn("denetim ?/?", satir)
            self.assertIn("claude ?", satir)

    def test_kok_bulunamazsa_cokmez(self):
        import io
        with mock.patch.object(sys, "stdin", io.StringIO("{}")), mock.patch.object(
                durum.Path, "resolve", side_effect=lambda *a, **k: Path("/yok/x")), mock.patch.object(
                kota_modulu_yukle := durum, "_kota_yukle", return_value=mock.Mock(kok_bul=mock.Mock(side_effect=SystemExit("x")))):
            with mock.patch.object(durum, "satir_uret", return_value="minimal") as su, mock.patch("builtins.print") as pr:
                self.assertEqual(durum.main(), 0)
            pr.assert_called_with("minimal")

    def test_git_onbellek(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            with mock.patch.object(durum, "git_degisiklik", return_value="4") as g:
                self.assertEqual(durum.git_onbellekli(d, d / "dur", 1000.0), "4")
                self.assertEqual(durum.git_onbellekli(d, d / "dur", 1010.0), "4")
                self.assertEqual(g.call_count, 1)
            with mock.patch.object(durum, "git_degisiklik", return_value="?"):
                self.assertEqual(durum.git_onbellekli(d, d / "dur", 1100.0), "4")  # zaman aşımı: eski değer

    def test_git_zaman_asimi_kisa(self):
        with mock.patch.object(durum.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 0.3)) as r:
            self.assertEqual(durum.git_degisiklik(Path("/yok")), "?")
        self.assertLessEqual(r.call_args[1]["timeout"], 0.3)

    def test_git_hatasi(self):
        with mock.patch.object(durum.subprocess, "run", side_effect=OSError):
            self.assertEqual(durum.git_degisiklik(Path("/yok")), "?")


class TakipTestleri(unittest.TestCase):
    SIM = datetime(2026, 10, 23, tzinfo=timezone.utc)

    def getir_fabrika(self):
        eski = (self.SIM - timedelta(days=30)).isoformat()
        yeni = (self.SIM - timedelta(days=2)).isoformat()

        def getir(url):
            if url.endswith("claude-code/latest") or "claude-code%2flatest" in url or url.endswith("%2fclaude-code/latest"):
                return json.dumps({"version": "2.2.0"}).encode()
            if "codex" in url:
                return json.dumps({"version": "0.5.0"}).encode()
            if "cc-safety-net" in url:
                return json.dumps({"time": {"created": eski, "2.6.12": eski, "2.7.0": eski, "2.8.0": yeni, "3.0.0-rc.1": eski}}).encode()
            if "releases.atom" in url:
                return (b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>v2.50.0</title>'
                        b'<link href="https://github.com/cli/cli/releases/tag/v2.50.0"/></entry></feed>')
            if "endoflife.date" in url:
                return json.dumps([{"cycle": "24", "latest": "24.1.0", "eol": "2028-04-30"},
                                   {"cycle": "18", "latest": "18.20.0", "eol": "2025-04-30"}]).encode()
            raise AssertionError(url)
        return getir

    def calistir_fabrika(self, surumler):
        def c(komut):
            if komut[0] not in surumler:
                raise OSError("yok")
            return surumler[komut[0]]
        return c

    def test_izlenenler_dosyasi_gercek_biçim(self):
        r = takip.izlenenleri_oku(NABIZ / "izlenenler.txt")
        adlar = [x["ad"] for x in r]
        self.assertEqual(adlar, ["claude", "codex", "opencode", "gh", "uv", "node", "cc-safety-net"])
        self.assertEqual(r[2]["tur"], "github")
        self.assertEqual(r[-1]["sabit"], "2.6.12")
        self.assertEqual(r[0]["komut"], ["claude", "--version"])

    def test_rapor_durumlari(self):
        izl = [
            {"ad": "claude", "tur": "npm", "kimlik": "@anthropic-ai/claude-code", "komut": ["claude"], "sabit": None},
            {"ad": "codex", "tur": "npm", "kimlik": "@openai/codex", "komut": ["codex"], "sabit": None},
            {"ad": "gh", "tur": "github", "kimlik": "cli/cli", "komut": ["gh"], "sabit": None},
            {"ad": "uv", "tur": "github", "kimlik": "x/uv", "komut": ["uv"], "sabit": None},
            {"ad": "node", "tur": "eol", "kimlik": "nodejs", "komut": ["node"], "sabit": None},
            {"ad": "cc-safety-net", "tur": "npm", "kimlik": "cc-safety-net", "komut": ["cc-safety-net"], "sabit": "2.6.12"},
        ]
        sur = {"claude": "2.1.0 (Claude Code)", "codex": "codex-cli 0.5.0", "gh": "gh version 2.50.0",
               "node": "v18.19.0", "cc-safety-net": "2.6.12"}
        metin, kod = takip.rapor_uret(izl, self.getir_fabrika(), self.calistir_fabrika(sur), self.SIM)
        self.assertIn("| claude | 2.1.0 | 2.2.0 | yeni sürüm var; elle incele |", metin)
        self.assertIn("| codex | 0.5.0 | 0.5.0 | güncel |", metin)
        self.assertIn("| gh | 2.50.0 | 2.50.0 | güncel |", metin)
        self.assertIn("| uv | yok | 2.50.0 | kurulu değil / okunamadı |", metin)
        self.assertIn("DESTEK BİTMİŞ", metin)
        # 7 günden yeni 2.8.0 aday olamaz; 3.0.0-rc.1 kararlı değil; aday 2.7.0
        self.assertIn("| cc-safety-net | 2.6.12 | 2.7.0 | sabit 2.6.12; aday 2.7.0", metin)
        self.assertEqual(kod, 1)

    def test_yama_farki_bilgi(self):
        o = {"ad": "gh", "tur": "github", "kimlik": "c", "komut": ["gh"], "sabit": None}
        self.assertEqual(takip.degerlendir(o, "2.103.0", "2.103.1", False), ("bilgi: yama farkı (2.103.1)", False))
        self.assertTrue(takip.degerlendir(o, "2.103.0", "2.104.0", False)[1])

    def test_hepsi_guncel_cikis_0(self):
        izl = [{"ad": "gh", "tur": "github", "kimlik": "cli/cli", "komut": ["gh"], "sabit": None}]
        _, kod = takip.rapor_uret(izl, self.getir_fabrika(), self.calistir_fabrika({"gh": "gh version 2.50.0"}), self.SIM)
        self.assertEqual(kod, 0)

    def test_cevrimdisi(self):
        def getir(url):
            raise takip.CevrimDisi("ağ yok")
        izl = [{"ad": "gh", "tur": "github", "kimlik": "cli/cli", "komut": ["gh"], "sabit": None}]
        metin, kod = takip.rapor_uret(izl, getir, self.calistir_fabrika({"gh": "2.50.0"}), self.SIM)
        self.assertIn("çevrimdışı", metin)
        self.assertEqual(kod, 1)

    def test_al_ag_hatasi_cevrimdisi_olur(self):
        import urllib.error
        with mock.patch.object(takip.urllib.request, "urlopen", side_effect=urllib.error.URLError("x")):
            with self.assertRaises(takip.CevrimDisi):
                takip.al("https://example.invalid/")

    def test_calistir_liste_argumani(self):
        with mock.patch.object(takip.subprocess, "run") as r:
            r.return_value = subprocess.CompletedProcess([], 0, "1.2.3\n", "")
            self.assertEqual(takip.calistir(["x", "--version"]), "1.2.3")
            self.assertIsInstance(r.call_args[0][0], list)
            self.assertNotIn("shell", r.call_args[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
