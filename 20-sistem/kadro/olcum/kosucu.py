"""Prepare offline tasks, print CLI commands, and append measurement records."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from destek import BASE, TASK_ROOT, TASKS, evaluate, expand_manifest


def prepare(task: str, target: Path) -> None:
    if target.exists() or target.is_symlink():
        raise ValueError("Hedef henüz mevcut olmamalı; girdiler üzerine yazılmaz.")
    expand_manifest(TASK_ROOT / task / "girdi.json", target)


def command(task: str, cli: str, model: str, effort: str, folder: Path) -> list[str]:
    prompt = (TASK_ROOT / task / "istem.md").read_text(encoding="utf-8")
    if cli == "codex":
        return ["codex", "exec", "-C", str(folder), "-s", "workspace-write", "-m", model,
                "-c", f"model_reasoning_effort={effort}", prompt]
    if cli == "agy":
        return ["agy", "-p", prompt, "--model", model, "--effort", effort,
                "--output-format", "stream-json", "--sandbox", "--mode", "accept-edits"]
    return ["opencode", "run", "-m", model, prompt]


def number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def quota_record(path: Path, cli: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Kota girdisi kota.py --json liste biçiminde olmalı.")
    matches = [item for item in data if isinstance(item, dict) and item.get("arac") == cli]
    if len(matches) != 1:
        raise ValueError("Kota girdisinde CLI için tek kayıt gerekli.")
    return matches[0]


def quota_delta(before: Path | None, after: Path | None, cli: str) -> tuple[dict | None, str]:
    if before is None and after is None:
        return None, "Kota ölçülmedi."
    if before is None or after is None:
        raise ValueError("Kota öncesi ve sonrası birlikte verilmeli.")
    first, last = quota_record(before, cli), quota_record(after, cli)
    differences = {}
    for window in ("5s", "hafta"):
        start = (first.get("pencereler") or {}).get(window)
        end = (last.get("pencereler") or {}).get(window)
        change = None
        if isinstance(start, dict) and isinstance(end, dict):
            initial, final = start.get("kullanilan"), end.get("kullanilan")
            reset = start.get("sifirlanma")
            if (number(initial) and number(final) and 0 <= initial <= final <= 1
                    and number(reset) and reset == end.get("sifirlanma")):
                change = round(final - initial, 10)
        differences[window] = change
    return differences, "Kota farkı kullanılan pay (0..1); bilinmeyen/sıfırlanan pencere null."


def measure(args: argparse.Namespace) -> dict:
    if not number(args.duration) or args.duration < 0:
        raise ValueError("Süre sonlu ve sıfırdan büyük ya da eşit olmalı.")
    delta, note = quota_delta(args.before, args.after, args.cli)
    outcome = evaluate(args.task, args.folder)
    now = datetime.now().astimezone()
    record = {
        "id": str(uuid4()), "tarih": now.isoformat(timespec="seconds"),
        "gorev": args.task, "cli": args.cli, "model": args.model, "efor": args.effort,
        "sure_sn": args.duration, "basari": outcome["basari"], "puan": outcome["puan"],
        "kota_farki": delta, "not": outcome["not"] + " " + note,
    }
    output = BASE.parent / "olcumler"
    if output.is_symlink() or any(path.is_symlink() for path in output.parents):
        raise ValueError("Günlük yolunda symlink var.")
    output.mkdir(exist_ok=True)
    path = output / f"{now.date().isoformat()}.jsonl"
    if path.is_symlink():
        raise ValueError("Günlük dosyası symlink olamaz.")
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ağ ve model çağrısı yapmayan ölçüm koşucusu")
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("hazirla", "degerlendir", "komut"):
        child = subparsers.add_parser(action)
        child.add_argument("task", choices=TASKS)
        child.add_argument("folder", type=Path)
        if action != "hazirla":
            child.add_argument("--cli", required=True, choices=("codex", "agy", "opencode"))
            child.add_argument("--model", required=True)
            child.add_argument("--efor", dest="effort", required=True)
        if action == "degerlendir":
            child.add_argument("--sure", dest="duration", required=True, type=float)
            child.add_argument("--kota-oncesi", dest="before", type=Path)
            child.add_argument("--kota-sonrasi", dest="after", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "hazirla":
            prepare(args.task, args.folder)
        elif args.action == "komut":
            print(json.dumps(command(args.task, args.cli, args.model, args.effort, args.folder), ensure_ascii=False))
        else:
            print(json.dumps(measure(args), ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(f"Hata: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
