#!/usr/bin/env python3
"""Offline tests for kutuphaneci.py. Run: python3 20-sistem/kutuphaneci/testler/kutuphaneci-testleri.py

Uses temp dirs only; subprocess.run is mocked; no network, no real home access.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

YOL = Path(__file__).resolve().parent.parent / "kutuphaneci.py"
spec = importlib.util.spec_from_file_location("kutuphaneci", YOL)
kt = importlib.util.module_from_spec(spec)
sys.modules["kutuphaneci"] = kt
spec.loader.exec_module(kt)

BUGUN = date(2026, 10, 23)


def sayfa(kok, yol, katman, son="2026-10-20", baglar="[]", baslik="Deneme", alanlar=True):
    p = Path(kok) / yol
    p.parent.mkdir(parents=True, exist_ok=True)
    if alanlar:
        on = (f"---\nkatman: {katman}  # yorum\nsurum: 1.0\nson_kontrol: {son}\n"
              f"kaynaklar: [https://a.example/x#y]\nbaglar: {baglar}\n---\n")
    else:
        on = f"---\nkatman: {katman}\n---\n"
    p.write_text(on + f"# {baslik}\n", encoding="utf-8")
    return p


def yeni_kok():
    d = tempfile.TemporaryDirectory()
    kok = Path(d.name)
    (kok / "00-cekirdek").mkdir()
    (kok / "00-cekirdek" / "ANAYASA.md").write_text("x", encoding="utf-8")
    return d, kok


def tamam(stdout="", stderr="", rc=0):
    return subprocess.CompletedProcess([], rc, stdout, stderr)


def agy_cikti(metin):
    return json.dumps({"event": "start"}) + "\n" + json.dumps({"event": "result", "result": {"response": metin}}) + "\n"


class OnMadde(unittest.TestCase):
    def test_parse(self):
        v = kt.on_madde_oku("---\nkatman: sistem # x\nbaglar: [a.md, ../b.md]\nkaynaklar: []\n---\n# T")
        self.assertEqual(v["katman"], "sistem")
        self.assertEqual(v["baglar"], ["a.md", "../b.md"])
        self.assertEqual(v["kaynaklar"], [])
        self.assertIsNone(kt.on_madde_oku("# yok"))
        self.assertIsNone(kt.on_madde_oku("---\nkatman: x\n"))

    def test_tirnakli_degerler(self):
        v = kt.on_madde_oku('---\nkatman: sistem\nsurum: "release #1"\nson_kontrol: \'2026-10-01\' # c\n'
                            'baglar: ["a,b.md", \'c.md\', d.md] # yorum\nkaynaklar: ["https://x/y#z"]\n---\n')
        self.assertEqual(v["surum"], "release #1")
        self.assertEqual(v["son_kontrol"], "2026-10-01")
        self.assertEqual(v["baglar"], ["a,b.md", "c.md", "d.md"])
        self.assertEqual(v["kaynaklar"], ["https://x/y#z"])

    def test_atomik_kayit_benzersiz_gecici(self):
        d, kok = yeni_kok()
        with d:
            yol = kok / "x" / "a.json"
            with mock.patch.object(kt.os, "replace", wraps=kt.os.replace) as rp:
                kt._kaydet(yol, {"a": 1})
                kt._kaydet(yol, {"a": 2})
            kaynaklar = [c.args[0] for c in rp.call_args_list]
            self.assertEqual(len(set(kaynaklar)), 2)
            self.assertTrue(all(k != str(yol) + ".tmp" for k in kaynaklar))
            self.assertEqual(json.loads(yol.read_text(encoding="utf-8")), {"a": 2})
            self.assertEqual([p.name for p in yol.parent.iterdir()], ["a.json"])

    def test_kok_bul(self):
        d, kok = yeni_kok()
        with d:
            (kok / "a" / "b").mkdir(parents=True)
            self.assertEqual(kt.kok_bul(kok / "a" / "b"), kok.resolve())


class Denetim(unittest.TestCase):
    def test_bulgular(self):
        d, kok = yeni_kok()
        with d:
            sayfa(kok, "10-donanim/monster/README.md", "donanim", baglar="[../../yok/README.md, ../../30-programlar/x/README.md]")
            sayfa(kok, "30-programlar/x/README.md", "programlar", son="2026-08-01")
            sayfa(kok, "30-programlar/y/README.md", "programlar", alanlar=False)
            (kok / "40-projeler" / "bos").mkdir(parents=True)
            ar = kok / "70-kutuphane" / "arastirmalar" / "konu"
            ar.mkdir(parents=True)
            (ar / "2026-10-01-a.md").write_text("# A\nKaynak denetimi: 9 sayfa\n[k](yok.md)\n", encoding="utf-8")
            (ar / "2026-10-02-b.md").write_text("# B\nsadece metin\n", encoding="utf-8")
            (kok / "70-kutuphane" / "arastirmalar" / "DIZIN.md").write_text(
                "- [a](konu/2026-10-01-a.md)\n", encoding="utf-8")
            s = kt.denetle(kok, bugun=BUGUN)
            kodlar = {(b["kod"], b["konu"]) for b in s["bulgular"]}
            self.assertIn(("kirik_bag", "10-donanim/monster/README.md → ../../yok/README.md"), kodlar)
            self.assertNotIn("30-programlar/x", " ".join(k[1] for k in kodlar if k[0] == "kirik_bag"))
            self.assertIn(("bayat_sayfa", "30-programlar/x/README.md"), kodlar)
            self.assertIn(("eksik_alan", "30-programlar/y/README.md"), kodlar)
            self.assertIn(("sayfa_yok", "40-projeler/bos"), kodlar)
            self.assertIn(("kirik_baglanti", "70-kutuphane/arastirmalar/konu/2026-10-01-a.md → yok.md"), kodlar)
            self.assertIn(("dizinsiz_rapor", "70-kutuphane/arastirmalar/konu/2026-10-02-b.md"), kodlar)
            self.assertIn(("kaynak_denetimi_yok", "70-kutuphane/arastirmalar/konu/2026-10-02-b.md"), kodlar)
            self.assertNotIn("kaynak_denetimi_yok", {k[0] for k in kodlar if k[1].endswith("-a.md")})
            self.assertEqual(sum(1 for k in kodlar if k[0] == "bayat_sayfa"), 1)

    def test_temiz(self):
        d, kok = yeni_kok()
        with d:
            sayfa(kok, "20-sistem/s/README.md", "sistem")
            self.assertEqual(kt.denetle(kok, bugun=BUGUN)["bulgular"], [])


class Kuyruk(unittest.TestCase):
    def test_tekrarsiz_ve_kapanma(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            (kok / "40-projeler" / "bos").mkdir(parents=True)
            q1 = kt.kuyruk(kok)
            q2 = kt.kuyruk(kok)
            self.assertEqual(len(q1), 1)
            self.assertEqual([i["id"] for i in q1], [i["id"] for i in q2])
            self.assertEqual(q1[0]["tur"], "sayfa_yaz")
            sayfa(kok, "40-projeler/bos/README.md", "projeler")
            q3 = kt.kuyruk(kok)
            self.assertEqual(q3[0]["durum"], "bitti")
            q4 = kt.kuyruk(kok, ekle=("arastir", "konu x"))
            self.assertEqual(sum(i["durum"] == "bekliyor" for i in q4), 1)

    def test_yeniden_acilma_ve_tur_kimligi(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            (kok / "40-projeler" / "bos").mkdir(parents=True)
            q = kt.kuyruk(kok)
            q[0]["durum"] = "bitti"  # worker finished but finding is still there
            kt._kaydet(kok / "durum" / "kuyruk.json", q)
            q = kt.kuyruk(kok)
            self.assertEqual(q[0]["durum"], "bekliyor")
            q = kt.kuyruk(kok, ekle=("arastir", "konu"))
            q = kt.kuyruk(kok, ekle=("haber", "konu"))
            elle = [i for i in q if i["kod"] == "elle"]
            self.assertEqual(len(elle), 2)
            self.assertEqual(len({i["id"] for i in elle}), 2)

    def test_kilit(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            with kt._kuyruk_kilidi(kok / "durum"):
                with self.assertRaises(BlockingIOError):
                    with kt._kuyruk_kilidi(kok / "durum"):
                        pass
                self.assertEqual(kt.calistir(kok), [])  # busy => exits quietly


class Calistir(unittest.TestCase):
    def kur(self, kok):
        (kok / "40-projeler" / "bos").mkdir(parents=True)
        kt.kuyruk(kok)

    def durum(self, kok):
        return json.loads((kok / "durum" / "kuyruk.json").read_text(encoding="utf-8"))

    def test_agy_basarili_ve_komut(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            self.kur(kok)
            with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "gizli", "OPENAI_API_KEY": "gizli"}), \
                    mock.patch.object(kt.subprocess, "run", return_value=tamam(agy_cikti("sayfa yazıldı"))) as run:
                kt.calistir(kok)
            self.assertEqual(run.call_count, 1)
            komut = run.call_args.args[0]
            self.assertIsInstance(komut, list)
            self.assertEqual(komut[0], "agy")
            for bayrak in ("--output-format", "stream-json", "--sandbox", "--dangerously-skip-permissions"):
                self.assertIn(bayrak, komut)
            self.assertIn("gemini-4-argon-high", komut)
            self.assertNotIn("shell", run.call_args.kwargs)
            self.assertIs(run.call_args.kwargs["stdin"], subprocess.DEVNULL)
            self.assertNotIn("ANTHROPIC_API_KEY", run.call_args.kwargs["env"])
            self.assertNotIn("OPENAI_API_KEY", run.call_args.kwargs["env"])
            self.assertTrue(run.call_args.kwargs["timeout"] > 0)
            is_ = self.durum(kok)[0]
            self.assertEqual((is_["durum"], is_["isci"], is_["sonuc"]), ("bitti", "agy", "sayfa yazıldı"))
            self.assertTrue((kok / "durum" / "gunluk.log").exists())

    def test_kota_sonraki_isciye(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            self.kur(kok)
            yanitlar = [tamam("", "Error 429 too many requests", 1), tamam("tamam", "", 0)]
            with mock.patch.object(kt.subprocess, "run", side_effect=yanitlar) as run:
                kt.calistir(kok)
            self.assertEqual([c.args[0][0] for c in run.call_args_list], ["agy", "claude"])
            self.assertIn("kutuphaneci", run.call_args_list[1].args[0])
            self.assertEqual(self.durum(kok)[0]["isci"], "claude")

    def test_hepsi_kota_bekliyor_codex_yok(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            self.kur(kok)
            with mock.patch.object(kt.subprocess, "run", return_value=tamam("", "usage limit reached", 1)) as run:
                kt.calistir(kok)
            self.assertNotIn("codex", [c.args[0][0] for c in run.call_args_list])
            self.assertEqual(self.durum(kok)[0]["durum"], "bekliyor")

    def test_zaman_asimi_ve_yok(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            self.kur(kok)
            with mock.patch.object(kt.subprocess, "run",
                                   side_effect=[subprocess.TimeoutExpired("agy", 1), FileNotFoundError()]):
                kt.calistir(kok)
            self.assertEqual(self.durum(kok)[0]["durum"], "bekliyor")

    def test_basarisiz(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            self.kur(kok)
            with mock.patch.object(kt.subprocess, "run", return_value=tamam("hata", "", 3)):
                kt.calistir(kok)
            self.assertEqual(self.durum(kok)[0]["durum"], "basarisiz")

    def test_codex_acik_istek_ve_kuru(self):
        d, kok = yeni_kok()
        with d, mock.patch.object(kt, "durum_klasoru", lambda k: k / "durum"):
            self.kur(kok)
            with mock.patch.object(kt.subprocess, "run") as run:
                kt.calistir(kok, kuru=True)
                run.assert_not_called()
            self.assertEqual(self.durum(kok)[0]["durum"], "bekliyor")
            with mock.patch.object(kt.subprocess, "run", return_value=tamam("ok")) as run:
                kt.calistir(kok, isci="codex")
            self.assertEqual(run.call_args.args[0][:2], ["codex", "exec"])
            self.assertIs(run.call_args.kwargs["stdin"], subprocess.DEVNULL)

    def test_istemler(self):
        for tur in kt.TURLER:
            metin = kt.istem_olustur({"tur": tur, "konu": "K", "katman": "sistem", "neden": "N", "dosyalar": ["a.md"]})
            self.assertIn("K", metin)
            self.assertNotIn("{{", metin)
            self.assertNotIn("/home/", metin)


class Harita(unittest.TestCase):
    def test_uret(self):
        d, kok = yeni_kok()
        with d:
            sayfa(kok, "10-donanim/monster/README.md", "donanim", baglar="[../../30-programlar/x/README.md]", baslik="Monster")
            sayfa(kok, "30-programlar/x/README.md", "programlar", baslik="X <b>")
            kt.harita(kok)
            md = (kok / "00-cekirdek" / "HARITA.md").read_text(encoding="utf-8")
            self.assertIn("## 10-donanim", md)
            self.assertIn("[Monster](../10-donanim/monster/README.md)", md)
            self.assertIn("bağ:", md)
            h = (kok / "50-arayuz" / "harita.html").read_text(encoding="utf-8")
            self.assertIn("<svg", h)
            self.assertIn("prefers-color-scheme", h)
            self.assertIn("X &lt;b&gt;", h)
            self.assertIn("<line", h)
            self.assertNotIn("http://", h.replace("http://www.w3.org", ""))
            self.assertNotIn("<script src", h)


class SablonVeKapsayici(unittest.TestCase):
    def test_sablon_ve_kapsayici_varlik_sayilmaz(self):
        d, kok = yeni_kok()
        (kok / "20-sistem" / "yayin" / "sablon").mkdir(parents=True)
        (kok / "20-sistem" / "yayin" / "sablon" / "x.md").write_text("---\nkatman: donanim\n---\n", encoding="utf-8")
        for ad in ("aktif", "deneme", "sablon"):
            (kok / "40-projeler" / ad).mkdir(parents=True, exist_ok=True)
        kodlar = {(b["kod"], b["konu"]) for b in kt.denetle(kok)["bulgular"]}
        self.assertFalse(any("sablon" in k for _, k in kodlar), kodlar)
        self.assertFalse(any(k.endswith(("40-projeler/aktif", "40-projeler/deneme")) for _, k in kodlar), kodlar)


class Gezin(unittest.TestCase):
    def test_ic_ice_repo_atlanir(self):
        d, kok = yeni_kok()
        with d:
            dis = kok / "70-kutuphane" / "arastirmalar"
            (dis / "konu").mkdir(parents=True)
            (dis / "a.md").write_text("x", encoding="utf-8")
            (dis / "konu" / "b.md").write_text("x", encoding="utf-8")
            repo = dis / "konu" / "proje"
            (repo / ".git").mkdir(parents=True)
            (repo / "c.md").write_text("x", encoding="utf-8")
            (repo / "alt").mkdir()
            (repo / "alt" / "d.md").write_text("x", encoding="utf-8")
            self.assertEqual({p.name for p in kt._gezin(dis)}, {"a.md", "b.md"})

    def test_baslangic_klasoru_repo_olsa_da_gezilir(self):
        d, kok = yeni_kok()
        with d:
            kok_repo = kok / "70-kutuphane" / "arastirmalar"
            (kok_repo / ".git").mkdir(parents=True)
            (kok_repo / "x.md").write_text("x", encoding="utf-8")
            self.assertEqual({p.name for p in kt._gezin(kok_repo)}, {"x.md"})


class RaporAtlama(unittest.TestCase):
    def test_readme_rapor_sayilmaz(self):
        d, kok = yeni_kok()
        with d:
            ar = kok / "70-kutuphane" / "arastirmalar"
            (ar / "konu").mkdir(parents=True)
            (ar / "README.md").write_text("# Kütüphane\n", encoding="utf-8")
            (ar / "konu" / "README.md").write_text("# Konu\n", encoding="utf-8")
            (ar / "DIZIN.md").write_text("- [a](konu/a.md)\n", encoding="utf-8")
            (ar / "konu" / "a.md").write_text("# A\nKaynak denetimi: 1 sayfa\n", encoding="utf-8")
            (ar / "konu" / "b.md").write_text("# B\nsadece metin\n", encoding="utf-8")
            kodlar = {(b["kod"], b["konu"]) for b in kt.denetle(kok, bugun=BUGUN)["bulgular"]}
            self.assertFalse(any("README.md" in konu for _, konu in kodlar), kodlar)
            self.assertIn(("dizinsiz_rapor", "70-kutuphane/arastirmalar/konu/b.md"), kodlar)
            self.assertIn(("kaynak_denetimi_yok", "70-kutuphane/arastirmalar/konu/b.md"), kodlar)


if __name__ == "__main__":
    unittest.main(verbosity=2)
