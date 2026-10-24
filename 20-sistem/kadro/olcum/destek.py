"""Shared deterministic checks for the offline measurement fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlsplit


TASKS = ("kod-duzeltme", "inceleme", "turkce-belge", "arastirma", "mekanik-tasima")
BASE = Path(__file__).resolve().parent
TASK_ROOT = BASE.parent / "gorevler"
EXPECTED = {'inceleme': [{'line': 2,
               'keywords': [['eval'],
                            ['kod', 'code', 'execution', 'calistir', 'guven', 'security']]},
              {'line': 8,
               'keywords': [['int', 'tamsayi', 'integer'],
                            ['ondalik', 'decimal', 'truncat', 'kesir', 'kurus', 'fraction']]},
              {'line': 10,
               'keywords': [['return', 'donus', 'doner'],
                            ['erken', 'early', 'ilk', 'first', 'dongu', 'loop']]}],
 'kod-duzeltme': {'test_sha256': 'd10eb2173e4e16c210315e9cfa8506978a6b6bd950050f0a97a693fe6988c752'},
 'mekanik-tasima': {'config': {'help': 'belgeler/kilavuz.md'},
                    'links': ['belgeler/kilavuz.md'],
                    'hashes': {'belgeler/kilavuz.md': '4b7711603470cd06111b72bc953bee6b6b31a8364363206d75ab3b53013c48c5',
                               'belgeler/README.md': '0b2a4c6fd7ff081eb878a09eccb0a14f4e51aaed6995e507d3c551d5657aecef'}}}


def expand_manifest(manifest: Path, target: Path) -> None:
    """Validate all paths before expanding UTF-8 text into a new directory."""
    entries = json.loads(read_text(manifest.parent, manifest.name))
    if not isinstance(entries, dict):
        raise ValueError("Manifest must be an object")
    paths = {}
    for name, content in entries.items():
        path = PurePosixPath(name)
        if (not name or not isinstance(content, str) or path.is_absolute()
                or PureWindowsPath(name).drive or "\\" in name
                or any(part in ("", ".", "..") for part in name.split("/"))):
            raise ValueError("Manifest requires relative file paths and text contents")
        paths[path] = content
    if any(parent in paths for path in paths for parent in path.parents):
        raise ValueError("Manifest file and directory paths conflict")
    if target.exists() or target.is_symlink():
        raise ValueError("Target must not exist")
    if any(parent.is_symlink() for parent in target.parents):
        raise ValueError("Symbolic links are not supported")
    target.mkdir(parents=True)
    for path, content in paths.items():
        destination = target.joinpath(*path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def read_text(folder: Path, name: str) -> str:
    path = folder / name
    if any(parent.is_symlink() for parent in path.parents):
        raise ValueError("Symbolic links are not supported")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Missing regular file: {name}")
    return path.read_text(encoding="utf-8")


def result(score: float, note: str) -> dict:
    return {"basari": score == 1.0, "puan": score, "not": note}


def digest(folder: Path, name: str) -> str:
    read_text(folder, name)
    return hashlib.sha256((folder / name).read_bytes()).hexdigest()


def check_code(folder: Path, fixture: Path) -> dict:
    expected = EXPECTED[fixture.name]
    if digest(folder, "testler.py") != expected["test_sha256"]:
        return result(0.0, "Test dosyasının SHA-256 özeti değişmiş.")
    read_text(folder, "guard.py")
    script = (
        "import sys, unittest; sys.path.insert(0, '.'); "
        "suite = unittest.defaultTestLoader.discover('.', pattern='testler.py'); "
        "outcome = unittest.TextTestRunner().run(suite); "
        "sys.exit(not outcome.wasSuccessful())"
    )
    process = subprocess.run(
        [sys.executable, "-I", "-B", "-c", script], cwd=folder,
        capture_output=True, text=True, timeout=10, check=False,
    )
    return result(float(process.returncode == 0),
                  "Testler geçti; test özeti aynı." if process.returncode == 0 else "Kod testleri başarısız.")


def normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold().replace("ı", "i"))
                   if not unicodedata.combining(c))


def check_review(folder: Path, fixture: Path) -> dict:
    findings = json.loads(read_text(folder, "bulgular.json"))["bulgular"]
    if not isinstance(findings, list):
        raise ValueError("bulgular must be a list")
    expected = EXPECTED[fixture.name]
    found = 0
    for issue in expected:
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            line = finding.get("satir")
            description = normalize(str(finding.get("aciklama", "")))
            if (type(line) is int and line == issue["line"]
                    and all(any(normalize(word) in description for word in group)
                            for group in issue["keywords"])):
                found += 1
                break
    return result(found / len(expected), f"{found}/{len(expected)} gömülü hata eşleşti; yanlış pozitifler ayrıca incelenir.")


def sections(text: str) -> dict[str, str]:
    parts = {}
    heading = None
    fenced = False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = re.fullmatch(r"## (.+)", line)
        if match:
            heading = match[1].strip()
            if heading in parts:
                raise ValueError("Duplicate section")
            parts[heading] = ""
        elif heading:
            parts[heading] += line + "\n"
    return parts


def check_document(folder: Path, fixture: Path) -> dict:
    text = read_text(folder, "README.md")
    parts = sections(text)
    required = ("Amaç", "Kullanım", "Girer", "Girmez", "Adlandırma")
    valid = text.startswith("# Not düzenleyici\n") and all(parts.get(h, "").strip() for h in required)
    return result(float(valid), "Yalnız yapı kontrol edildi; içerik rubriği farklı sağlayıcıdan bekleniyor.")


def check_research(folder: Path, fixture: Path) -> dict:
    text = read_text(folder, "rapor.md")
    parts = sections(text)
    summary = parts.get("Özet", "").strip()
    sources = parts.get("Kaynaklar", "").strip().splitlines()
    ids = []
    valid = bool(summary) and len(summary.split()) <= 180 and len(sources) >= 2
    for source in sources:
        match = re.fullmatch(r"\[(\d+)\] (https?://\S+)", source.strip())
        if not match:
            valid = False
            continue
        identifier, url = match.groups()
        parsed = urlsplit(url)
        valid = valid and bool(parsed.hostname) and not parsed.username and not parsed.password
        ids.append(identifier)
    citations = set(re.findall(r"\[(\d+)\]", summary))
    valid = valid and len(ids) == len(set(ids)) and set(ids) == citations
    return result(float(bool(valid)), "Yalnız kaynak satırı, URL ve atıf biçimi kontrol edildi; doğruluk doğrulanmadı.")


def check_move(folder: Path, fixture: Path) -> dict:
    checklist = EXPECTED[fixture.name]
    errors = []
    for name, expected in checklist["hashes"].items():
        if digest(folder, name) != expected:
            errors.append(f"İçerik değişmiş: {name}")
    config = json.loads(read_text(folder, "ayar.json"))
    if config != checklist["config"]:
        errors.append("Ayar yolları kontrol listesiyle eşleşmiyor")
    links = re.findall(r"\]\(([^)]+)\)", read_text(folder, "README.md"))
    if links != checklist["links"]:
        errors.append("README bağları kontrol listesiyle eşleşmiyor")
    for name in checklist["links"]:
        read_text(folder, name)
    return result(float(not errors), "; ".join(errors) if errors else "Kontrol listesi: 0 hata.")


CHECKS = dict(zip(TASKS, (check_code, check_review, check_document, check_research, check_move)))


def evaluate(task: str, folder: Path) -> dict:
    try:
        return CHECKS[task](folder, TASK_ROOT / task)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        return result(0.0, f"Değerlendirme başarısız: {type(error).__name__}")


def evaluator_main(task: str) -> None:
    parser = argparse.ArgumentParser(description="Çevrimdışı görev değerlendirmesi")
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(task, args.folder), ensure_ascii=False, allow_nan=False))
