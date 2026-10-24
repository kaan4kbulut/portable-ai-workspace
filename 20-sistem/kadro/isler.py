#!/usr/bin/env python3
"""Job registry + watchdog + terminal dashboard for worker CLIs (codex, agy, opencode, local, claude).

Usage:
  python3 20-sistem/kadro/isler.py baslat --gorev "..." --arac codex --model gpt-6-sol --efor high \
      [--ajan AD] [--klasor DIR] [--sure 3600] [--hareketsiz 180] -- <command ...>
  python3 20-sistem/kadro/isler.py pano [--izle]     # dashboard; --izle refreshes every 2 s
  python3 20-sistem/kadro/isler.py ozet              # one-line summary for the status line

Every job gets 20-sistem/durum/<host>/isler/<id>.json (state) and <id>.log (worker stdout+stderr).
The worker always runs with stdin=/dev/null in its own process group. It is killed when the log and the
work folder stop changing for --hareketsiz seconds (state "takildi") or after --sure seconds ("zaman_asimi").
Exit code 0 alone is not success: an empty log or a refused tool action marks the job "basarisiz".
Stdlib only; no network.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DIZIN = Path(__file__).resolve().parent
KOK = DIZIN.parents[1]
YOKLAMA_S = 2
# refusals / limits printed by the CLIs while still exiting 0
# Only structured error events and failing exits are inspected: worker logs quote code and tests that contain
# words like "429" or "denied_actions" (2026-10-24: a codex job writing 429 tests was misreported as "limit").
RET_METNI = re.compile(r"Permission required|permission denied by|Model unavailable", re.I)
LIMIT_IMZASI = re.compile(r"\b429\b|rate.?limit|usage limit|quota exceeded|limit reached|resource.?exhausted", re.I)
SIMGE = {"sirada": "⏳ sırada", "calisiyor": "▶ çalışıyor", "bitti": "✔ bitti", "basarisiz": "✖ başarısız",
         "takildi": "⚠ takıldı", "zaman_asimi": "⌛ zaman aşımı", "reddedildi": "⛔ reddedildi", "limit": "⛔ limit",
         "gecti": "↪ geçti"}


def _kota():
    spec = importlib.util.spec_from_file_location("isler_kota", KOK / "20-sistem" / "nabiz" / "kota.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_klasoru() -> Path:
    d = _kota().durum_klasoru(KOK) / "isler"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _yaz(yol: Path, veri: dict) -> None:
    gecici = yol.with_name(f".{yol.name}.{os.getpid()}.tmp")
    gecici.write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(gecici, yol)


def yeni_kimlik(d: Path) -> str:
    sayilar = [int(m.group(1)) for p in d.glob("k*.json") if (m := re.fullmatch(r"k(\d+)\.json", p.name))]
    return f"k{max(sayilar, default=0) + 1}"


def reserve_record(directory: Path) -> str:
    """Reserve a dashboard row without racing another executor."""
    directory.mkdir(parents=True, exist_ok=True)
    while True:
        identity = yeni_kimlik(directory)
        try:
            with (directory / f"{identity}.json").open("x", encoding="utf-8") as stream:
                json.dump({"id": identity, "durum": "sirada", "baslangic": time.time()}, stream)
            return identity
        except FileExistsError:
            continue


def _son_satir(log: Path, boyut: int = 4096) -> str:
    try:
        with open(log, "rb") as f:
            f.seek(max(0, log.stat().st_size - boyut))
            satirlar = [s.strip() for s in f.read().decode("utf-8", "replace").splitlines() if s.strip()]
    except OSError:
        return ""
    if not satirlar:
        return ""
    s = satirlar[-1]
    try:  # stream-json / jsonl: show something readable
        o = json.loads(s)
        su = o.get("step_update") or {}
        s = (su.get("tool_name") or su.get("step_type") or o.get("type") or o.get("event") or s)
        if su.get("text_delta"):
            s += ": " + su["text_delta"]
    except (ValueError, AttributeError):
        pass
    return re.sub(r"\s+", " ", str(s))[:90]


def _klasor_mtime(klasor: Path | None, sinir: int = 4000) -> float:
    """Newest mtime under the work folder (skips .git); bounded walk so a large tree cannot stall the watchdog."""
    if not klasor or not klasor.is_dir():
        return 0.0
    en, sayac = 0.0, 0
    for kok, dizinler, dosyalar in os.walk(klasor):
        dizinler[:] = [x for x in dizinler if x not in (".git", "node_modules", "__pycache__")]
        for ad in dosyalar:
            sayac += 1
            try:
                en = max(en, os.stat(os.path.join(kok, ad)).st_mtime)
            except OSError:
                pass
            if sayac >= sinir:
                return en
    return en


def run_worker(a, directory: Path | None = None, env: dict | None = None,
               root: Path | None = None, on_started=None) -> dict:
    """Run the shared watchdog and return its persisted row without printing."""
    d = directory if directory is not None else is_klasoru()
    d.mkdir(parents=True, exist_ok=True)
    kimlik = reserve_record(d)
    durum_yolu, log = d / f"{kimlik}.json", d / f"{kimlik}.log"
    klasor = Path(a.klasor).resolve() if a.klasor else None
    is_ = {"id": kimlik, "gorev": a.gorev, "arac": a.arac, "ajan": a.ajan or "-", "model": a.model or "varsayilan",
           "efor": a.efor or "-", "klasor": os.path.relpath(klasor, root or KOK) if klasor else "",
           "komut": Path(a.komut[0]).name if a.komut else "",
           "durum": "calisiyor", "baslangic": time.time(), "bitis": None, "cikis": None, "neden": "",
           "son_olay": "", "son_olay_zamani": time.time(), "pid": None, "log": log.name}
    with open(log, "wb") as cikti:
        try:
            p = subprocess.Popen(a.komut, stdin=subprocess.DEVNULL, stdout=cikti, stderr=subprocess.STDOUT,
                                 cwd=str(klasor) if klasor else None, env=env, start_new_session=True)
        except OSError as e:
            is_.update(durum="basarisiz", neden=f"başlatılamadı: {e}", bitis=time.time())
            _yaz(durum_yolu, is_)
            return is_
    is_["pid"] = p.pid
    _yaz(durum_yolu, is_)
    if on_started is not None:
        on_started(is_)
    son_boyut, son_mtime, son_hareket = -1, _klasor_mtime(klasor), time.time()
    while True:
        rc = p.poll()
        simdi = time.time()
        boyut = log.stat().st_size if log.exists() else 0
        mtime = _klasor_mtime(klasor)
        if boyut != son_boyut or mtime > son_mtime:
            son_boyut, son_mtime, son_hareket = boyut, max(mtime, son_mtime), simdi
            is_.update(son_olay=_son_satir(log), son_olay_zamani=simdi)
        if rc is not None:
            break
        if simdi - son_hareket > a.hareketsiz or simdi - is_["baslangic"] > a.sure:
            asim = simdi - is_["baslangic"] > a.sure
            is_.update(durum="zaman_asimi" if asim else "takildi",
                       neden=f"{a.sure} sn mutlak süre doldu" if asim else f"{a.hareketsiz} sn hareketsiz (günlük ve klasör değişmedi)")
            try:
                os.killpg(p.pid, signal.SIGTERM)
                try:
                    p.wait(10)
                except subprocess.TimeoutExpired:
                    pass
                # Descendants may survive after their parent exits on SIGTERM.
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            p.wait()
            rc = p.returncode
            break
        _yaz(durum_yolu, is_)
        time.sleep(YOKLAMA_S)
    metin = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    is_.update(cikis=rc, bitis=time.time(), son_olay=_son_satir(log) or is_["son_olay"])
    if is_["durum"] == "calisiyor":
        durum, neden = sinifla(metin, rc)
        is_.update(durum=durum, neden=neden)
    _yaz(durum_yolu, is_)
    return is_


def sinifla(metin: str, rc: int | None) -> tuple[str, str]:
    """(state, reason) from a finished worker log; structured events first, free text only on failure."""
    olaylar = []
    for satir in metin.splitlines():
        satir = satir.strip()
        if satir.startswith("{"):
            try:
                o = json.loads(satir)
            except ValueError:
                continue
            if isinstance(o, dict):
                olaylar.append(o)
    for o in olaylar:
        r = o.get("result") if o.get("event") == "result" else None
        if isinstance(r, dict):
            if r.get("denied_actions"):
                return "reddedildi", "araç eylemi reddedildi (agy result.denied_actions; çıkış kodu ne olursa olsun)"
            if r.get("error") or str(r.get("status", "SUCCESS")).upper() not in ("SUCCESS", ""):
                hata = json.dumps(r.get("error") or r.get("status"), ensure_ascii=False)
                return ("limit" if LIMIT_IMZASI.search(hata) else "basarisiz"), f"agy sonucu: {hata[:120]}"
        if o.get("type") in ("turn.failed", "error"):
            hata = json.dumps(o, ensure_ascii=False)
            return ("limit" if LIMIT_IMZASI.search(hata) else "basarisiz"), f"codex {o.get('type')}: {hata[:120]}"
        if o.get("type") == "error" or (o.get("type") == "session.error"):
            hata = json.dumps(o, ensure_ascii=False)
            return ("limit" if LIMIT_IMZASI.search(hata) else "basarisiz"), f"hata olayı: {hata[:120]}"
    kuyruk = "\n".join(metin.strip().splitlines()[-5:])
    if rc not in (0, None):
        if LIMIT_IMZASI.search(kuyruk):
            return "limit", f"çıkış {rc}, limit imzası"
        return "basarisiz", f"çıkış {rc}"
    if not metin.strip():
        return "basarisiz", "çıkış 0 ama çıktı boş"
    hata_satiri = [x for x in kuyruk.splitlines() if re.match(r"^\W*(Error|error|ERROR)\b", x)]
    if LIMIT_IMZASI.search(kuyruk) and (len(metin) < 4000 or any(LIMIT_IMZASI.search(x) for x in hata_satiri)):
        return "limit", "çıkış 0 ama limit hatasıyla bitti: " + kuyruk.splitlines()[-1][:100]
    if RET_METNI.search(kuyruk) or re.search(r"^\W*Error:", kuyruk, re.M):
        return "basarisiz", "çıkış 0 ama son satırlarda hata: " + kuyruk.splitlines()[-1][:100]
    return "bitti", ""


def baslat(a) -> int:
    row = run_worker(a, on_started=lambda row: print(row["id"], flush=True))
    if row["cikis"] is None:
        print(f"{row['id']} başarısız: {row['neden']}", file=sys.stderr)
        return 2
    return 0 if row["durum"] == "bitti" else 1


def isleri_oku(d: Path) -> list[dict]:
    out = []
    for p in d.glob("k*.json"):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    for i in out:  # a dead watchdog leaves "calisiyor" behind: show it honestly
        if i.get("durum") == "calisiyor" and i.get("pid"):
            try:
                os.kill(i["pid"], 0)
            except OSError:
                i["durum"], i["neden"] = "basarisiz", "süreç yok, izleyici kaydı kapatmadı"
    return sorted(out, key=lambda i: i.get("baslangic") or 0, reverse=True)


def _sure(i: dict) -> str:
    s = int((i.get("bitis") or time.time()) - (i.get("baslangic") or time.time()))
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"


def _gpu() -> str:
    if not shutil.which("nvidia-smi"):
        return "GPU yok"
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,power.draw",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2, check=False)
        k, m, w = [x.strip() for x in p.stdout.split(",")[:3]]
        return f"GPU %{k} · {int(float(m)) / 1024:.1f} GB · {float(w):.0f} W"
    except (OSError, ValueError, subprocess.SubprocessError):
        return "GPU ?"


def kota_satiri() -> str:
    k = _kota()
    simdi = time.time()
    satirlar = [k.claude_oku(KOK, simdi), k.codex_oku(simdi), k.agy_oku(KOK, simdi, yenile=False),
                k.agy_oku(KOK, simdi, yenile=False, grup="claude")]
    parca = []
    for s in satirlar:
        if s.get("kalan_yuzde") is None:
            parca.append(f"{s['arac']} ?")
            continue
        p = s.get("pencereler") or {}
        w = " ".join(f"{e}%{k.kalan_yuzde(p[a], None, simdi)}" for a, e in (("5s", "5s"), ("hafta", "hf")) if p.get(a))
        parca.append(f"{s['arac']} {w}")
    return " · ".join(parca) + " · opencode ücretsiz"


def pano_metni(genislik: int = 100, sinir: int = 15) -> str:
    isler = isleri_oku(is_klasoru())
    ciz = "─" * min(genislik, 110)
    sat = [f"kaan4kbulut · işler{'':>{max(1, min(genislik, 110) - 28)}}{datetime.now():%H:%M:%S}", ciz,
           "KOTA  " + kota_satiri(), "      " + _gpu(), ciz,
           f"{'ID':<5}{'GÖREV':<24}{'ARAÇ':<9}{'MODEL':<20}{'EFOR':<7}{'DURUM':<15}SÜRE"]
    for i in isler[:sinir]:
        sat.append(f"{i['id']:<5}{str(i.get('gorev', ''))[:23]:<24}{str(i.get('arac', ''))[:8]:<9}"
                   f"{str(i.get('model', ''))[:19]:<20}{str(i.get('efor', ''))[:6]:<7}"
                   f"{SIMGE.get(i.get('durum'), i.get('durum', '')):<15}{_sure(i)}")
        if i.get("neden"):
            sat.append(f"{'':<10}↳ {i['neden'][:90]}")
    if not isler:
        sat.append("(henüz kayıtlı iş yok)")
    sat.append(ciz)
    calisan = [i for i in isler if i.get("durum") == "calisiyor"]
    if calisan:
        i = max(calisan, key=lambda x: x.get("son_olay_zamani") or 0)
        once = int(time.time() - (i.get("son_olay_zamani") or time.time()))
        sat.append(f"son olay: {i['id']} · {once} sn önce · {i.get('son_olay') or '-'}")
    return "\n".join(sat)


def ozet() -> str:
    isler = isleri_oku(is_klasoru())
    c = sum(1 for i in isler if i.get("durum") == "calisiyor")
    sorun = sum(1 for i in isler[:20] if i.get("durum") in ("takildi", "zaman_asimi", "reddedildi", "limit", "basarisiz")
                and time.time() - (i.get("bitis") or 0) < 3600)
    return f"işler {c}▶" + (f" {sorun}⚠" if sorun else "")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="İş kaydı, bekçi ve pano")
    alt = ap.add_subparsers(dest="komut_adi", required=True)
    b = alt.add_parser("baslat")
    b.add_argument("--gorev", required=True)
    b.add_argument("--arac", required=True)
    b.add_argument("--model")
    b.add_argument("--efor")
    b.add_argument("--ajan")
    b.add_argument("--klasor")
    b.add_argument("--sure", type=int, default=3600)
    b.add_argument("--hareketsiz", type=int, default=180)
    b.add_argument("komut", nargs=argparse.REMAINDER)
    p = alt.add_parser("pano")
    p.add_argument("--izle", action="store_true")
    alt.add_parser("ozet")
    a = ap.parse_args(argv)
    if a.komut_adi == "baslat":
        if a.komut and a.komut[0] == "--":
            a.komut = a.komut[1:]
        if not a.komut:
            ap.error("'--' sonrasında çalıştırılacak komut gerekli")
        return baslat(a)
    if a.komut_adi == "ozet":
        print(ozet())
        return 0
    if not a.izle:
        print(pano_metni(shutil.get_terminal_size((100, 30)).columns))
        return 0
    try:
        while True:
            metin = pano_metni(shutil.get_terminal_size((100, 30)).columns)
            sys.stdout.write("\033[H\033[2J" + metin + "\n")
            sys.stdout.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
