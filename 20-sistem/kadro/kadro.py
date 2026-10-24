#!/usr/bin/env python3
"""Select model/effort candidates and learn from offline measurements."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time

sys.dont_write_bytecode = True

CONFIG_PATH = Path(__file__).resolve().with_name("kadro.json")
TASK_TYPES = (
    "kod-duzeltme", "inceleme", "turkce-belge", "arastirma", "mekanik-tasima", "basit",
)
EFFORTS = {"low": 0, "medium": 1, "high": 2}
QUOTA_MODES = {"bol": 0, "normal": 1, "idareli": 2}
MEASUREMENT_FIELDS = {
    "gorev", "cli", "model", "efor", "sure_sn", "basari", "puan", "kota_farki", "not",
}


class InputError(ValueError):
    """An input failed validation without changing persistent state."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def is_number(value: object) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def valid_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def reject_constant(value: str) -> None:
    raise InputError("JSON içinde sonlu olmayan sayı var")


def unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "JSON içinde yinelenen alan var")
        result[key] = value
    return result


def decode_json(text: str) -> object:
    return json.loads(text, parse_constant=reject_constant, object_pairs_hook=unique_object)


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def measurement_key(task_type: str, candidate: dict) -> str:
    return canonical([task_type, candidate["cli"], candidate["model"], candidate["efor"]])


def validate_candidate(candidate: object, providers: dict) -> None:
    require(isinstance(candidate, dict), "aday nesne olmalı")
    require(set(candidate) == {"cli", "model", "efor"}, "aday alanları geçersiz")
    require(valid_text(candidate["cli"]) and candidate["cli"] in providers,
            "aday CLI sağlayıcı eşlemesinde yok")
    require(valid_text(candidate["model"]), "model boş olamaz")
    require(isinstance(candidate["efor"], str) and candidate["efor"] in EFFORTS,
            "efor low, medium veya high olmalı")


def validate_config(config: object) -> dict:
    require(isinstance(config, dict), "kadro nesne olmalı")
    require(type(config.get("surum")) is int and config["surum"] == 1, "kadro sürümü geçersiz")
    require(config.get("inceleme_saglayici_farkli") is True,
            "incelemede farklı sağlayıcı zorunlu")
    providers = config.get("saglayicilar")
    require(isinstance(providers, dict) and bool(providers), "sağlayıcı eşlemesi eksik")
    require(all(valid_text(key) and valid_text(value) for key, value in providers.items()),
            "sağlayıcı eşlemesi geçersiz")
    for field in ("is_turu", "yedek"):
        groups = config.get(field)
        require(isinstance(groups, dict) and set(groups) == set(TASK_TYPES),
                f"{field}: altı iş türü gerekli")
        for candidates in groups.values():
            require(isinstance(candidates, list), f"{field}: aday listesi gerekli")
            for candidate in candidates:
                validate_candidate(candidate, providers)
            require(len({canonical(item) for item in candidates}) == len(candidates),
                    "aday listesinde tekrar var")
    hard_tasks = config.get("zor_isler")
    require(isinstance(hard_tasks, list)
            and all(isinstance(item, str) and item in TASK_TYPES for item in hard_tasks),
            "zor iş listesi geçersiz")
    stats = config.get("olcumler")
    require(isinstance(stats, dict), "ölçüm sayaçları eksik")
    for key, record in stats.items():
        identity = decode_json(key)
        require(isinstance(identity, list) and len(identity) == 4,
                "ölçüm anahtarı geçersiz")
        require(isinstance(identity[0], str) and identity[0] in TASK_TYPES,
                "ölçüm iş türü geçersiz")
        validate_candidate(dict(zip(("cli", "model", "efor"), identity[1:])), providers)
        require(key == canonical(identity), "ölçüm anahtarı kanonik değil")
        require(isinstance(record, dict), "ölçüm sayacı nesne olmalı")
        count = record.get("n")
        require(type(count) is int and count > 0, "ölçüm sayısı pozitif tam sayı olmalı")
        for field in ("toplam_puan", "toplam_sure_sn", "toplam_kota_farki"):
            require(is_number(record.get(field)), "ölçüm toplamı sonlu sayı olmalı")
        require(0 <= record["toplam_puan"] <= count and record["toplam_sure_sn"] >= 0,
                "ölçüm toplamı aralık dışında")
    processed = config.get("islenmis_sonuclar")
    require(isinstance(processed, dict), "işlenmiş sonuç kimlikleri eksik")
    require(all(valid_text(key) and isinstance(value, str) and len(value) == 64
                and all(char in "0123456789abcdef" for char in value)
                for key, value in processed.items()), "işlenmiş sonuç kimliği geçersiz")
    return config


def load_config(path: Path = CONFIG_PATH) -> dict:
    return validate_config(decode_json(path.read_text(encoding="utf-8")))


def load_quotas(root: Path | None = None) -> list[dict]:
    """Reuse the quota reader while disabling its CLI refresh path."""
    root = root or CONFIG_PATH.parents[2]
    path = root / "20-sistem" / "nabiz" / "kota.py"
    spec = importlib.util.spec_from_file_location("roster_quota", path)
    require(spec is not None and spec.loader is not None, "kota okuyucusu yüklenemedi")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.hepsi(root, agy=False)
    rows.append(module.agy_oku(root, time.time(), yenile=False))  # cache only, never runs agy
    return rows


def quota_index(rows: object) -> dict:
    require(isinstance(rows, list), "kota girdisi liste olmalı")
    indexed = {}
    for row in rows:
        require(isinstance(row, dict) and valid_text(row.get("arac")), "kota satırı geçersiz")
        require(row["arac"] not in indexed, "aynı CLI için birden fazla kota satırı var")
        require(isinstance(row.get("kip"), str), "kota kipi eksik")
        require(row.get("baglayici") in (None, "5s", "hafta"), "bağlayıcı pencere geçersiz")
        remaining = row.get("kalan_yuzde")
        require(remaining is None or (is_number(remaining) and 0 <= remaining <= 100),
                "kalan kota yüzdesi geçersiz")
        require(isinstance(row.get("pencereler"), dict), "kota pencereleri eksik")
        indexed[row["arac"]] = dict(row)
    return indexed


def provider_for(candidate: dict, config: dict) -> str:
    if candidate["cli"] == "agy" and candidate["model"].lower().startswith("claude-"):
        return "anthropic"
    return config["saglayicilar"][candidate["cli"]]


def score_candidate(task_type: str, candidate: dict, position: int, config: dict) -> dict:
    prior = max(0.5, 0.75 - 0.05 * position)
    record = config["olcumler"].get(measurement_key(task_type, candidate), {})
    count = record.get("n", 0)
    mean = record["toplam_puan"] / count if count else None
    alpha = count / (count + 5)
    score = (1 - alpha) * prior + alpha * (mean if mean is not None else prior)
    return {"n": count, "onsel": prior, "ortalama": mean, "a": alpha, "puan": score}


def select(task_type: str, config: dict, quotas: list[dict],
           writer_provider: str | None = None) -> dict:
    require(task_type in TASK_TYPES, "bilinmeyen iş türü")
    validate_config(config)
    indexed = quota_index(quotas)
    result = {"is_turu": task_type, "durum": "uygun_aday_yok", "aday": None,
              "gerekce": "Uygun aday yok.", "elenenler": [], "bilinmeyenler": []}
    if task_type == "inceleme" and not valid_text(writer_provider):
        result.update(durum="yazan_saglayici_gerekli",
                      gerekce="Farklı sağlayıcı denetimi için --yazan-saglayici gerekli.")
        return result
    for group in ("is_turu", "yedek"):
        eligible = []
        for position, candidate in enumerate(config[group][task_type]):
            provider = provider_for(candidate, config)
            quota = indexed.get(candidate["cli"], {
                "arac": candidate["cli"], "baglayici": None, "kalan_yuzde": None,
                "kip": "bilinmiyor", "pencereler": {},
            })
            mode = quota["kip"]
            entry = {"aday": dict(candidate), "saglayici": provider, "kota": quota,
                     "grup": group}
            reason = None
            if task_type == "inceleme" and provider == writer_provider:
                reason = "Yazanla aynı sağlayıcı."
            elif mode == "dolu":
                reason = "CLI kotası dolu."
            elif (mode == "idareli" and task_type != "inceleme"
                  and task_type not in config["zor_isler"]):
                reason = "İdareli kota yalnız zor iş veya inceleme için kullanılabilir."
            elif mode not in QUOTA_MODES:
                reason = "Kota bilinmiyor veya desteklenmeyen kip; otomatik seçilmedi."
                result["bilinmeyenler"].append(entry)
            if reason:
                result["elenenler"].append({**entry, "gerekce": reason})
                continue
            evidence = score_candidate(task_type, candidate, position, config)
            entry["olcum"] = evidence
            eligible.append((QUOTA_MODES[mode], -evidence["puan"],
                             EFFORTS[candidate["efor"]], position, entry))
        if eligible:
            selected = min(eligible, key=lambda item: item[:4])[-1]
            quota, evidence = selected["kota"], selected["olcum"]
            reason = (f"{'Yedek' if group == 'yedek' else 'Ana'} aday; "
                      f"kota={quota['kip']}, bağlayıcı={quota['baglayici']}, "
                      f"kalan=%{quota['kalan_yuzde']}; n={evidence['n']}, "
                      f"önsel={evidence['onsel']:.3f}, "
                      f"ölçüm={evidence['ortalama']}, a={evidence['a']:.3f}, "
                      f"puan={evidence['puan']:.3f}.")
            result.update(durum="secildi", aday=selected["aday"],
                          saglayici=selected["saglayici"], kota=quota,
                          olcum=evidence, yedek=group == "yedek", gerekce=reason)
            return result
    if result["bilinmeyenler"]:
        result["gerekce"] += " Kotası bilinmeyen adaylar var; doğrulama gerekiyor."
    return result


def validate_measurement(row: object, config: dict) -> dict:
    require(isinstance(row, dict), "ölçüm satırı nesne olmalı")
    require(MEASUREMENT_FIELDS <= set(row) <= MEASUREMENT_FIELDS | {"id"},
            "ölçüm alanları eksik veya bilinmeyen alan var")
    require(isinstance(row["gorev"], str) and row["gorev"] in TASK_TYPES,
            "gorev alanı kayıtlı iş türü olmalı")
    validate_candidate({key: row[key] for key in ("cli", "model", "efor")},
                       config["saglayicilar"])
    require(is_number(row["sure_sn"]) and row["sure_sn"] >= 0, "süre geçersiz")
    success, rating = row["basari"], row["puan"]
    require(success is None or isinstance(success, bool)
            or (is_number(success) and 0 <= success <= 1), "başarı 0–1 veya null olmalı")
    require(rating is None or (is_number(rating) and 0 <= rating <= 5),
            "puan 0–5 veya null olmalı")
    require(success is not None or rating is not None, "başarı veya puan gerekli")
    require(row["kota_farki"] is None or is_number(row["kota_farki"]),
            "kota farkı sonlu sayı veya null olmalı")
    require(isinstance(row["not"], str), "not metin olmalı")
    require("id" not in row or valid_text(row["id"]), "id boş olamaz")
    normalized = dict(row)
    for field in ("sure_sn", "basari", "puan", "kota_farki"):
        if normalized[field] is not None:
            normalized[field] = float(normalized[field])
            if normalized[field] == 0:
                normalized[field] = 0.0
    return normalized


def read_measurements(path: Path, config: dict) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(validate_measurement(decode_json(line), config))
        except (ValueError, TypeError) as error:
            raise InputError(f"Ölçüm satırı {line_number}: geçersiz JSON veya alan ({type(error).__name__})") from None
    require(bool(rows), "ölçüm dosyası boş")
    return rows


@contextmanager
def config_lock(path: Path):
    lock = path.with_name("kadro-kilit.tmp")
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise InputError("Öğrenme kilidi var; başka yazıcıyı veya kesilmiş oturumu denetleyin.") from None
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def atomic_write(path: Path, config: dict) -> None:
    content = json.dumps(config, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="kadro-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def learn(source: Path, config_path: Path = CONFIG_PATH) -> dict:
    with config_lock(config_path):
        config = load_config(config_path)
        rows = read_measurements(source, config)
        added = repeated = 0
        for row in rows:
            payload = {key: value for key, value in row.items() if key != "id"}
            fingerprint = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
            identity = row.get("id", "sha256:" + fingerprint)
            processed = config["islenmis_sonuclar"]
            if identity in processed:
                require(processed[identity] == fingerprint, "aynı id farklı ölçümle kullanılmış")
                repeated += 1
                continue
            key = measurement_key(row["gorev"], row)
            record = config["olcumler"].setdefault(key, {
                "n": 0, "toplam_puan": 0.0, "toplam_sure_sn": 0.0, "toplam_kota_farki": 0.0,
            })
            components = [value for value in (row["basari"],
                          None if row["puan"] is None else row["puan"] / 5) if value is not None]
            record["n"] += 1
            record["toplam_puan"] += sum(components) / len(components)
            record["toplam_sure_sn"] += row["sure_sn"]
            record["toplam_kota_farki"] += row["kota_farki"] or 0.0
            processed[identity] = fingerprint
            added += 1
        validate_config(config)
        if added:
            atomic_write(config_path, config)
    return {"eklenen": added, "tekrar": repeated}


def format_result(result: dict) -> str:
    candidate = result["aday"]
    triple = (f"{candidate['cli']} / {candidate['model']} / {candidate['efor']}"
              if candidate else "uygun aday yok")
    lines = [f"{result['is_turu']}: {triple}", f"  {result['gerekce']}"]
    for entry in result["elenenler"]:
        lines.append(f"  Elendi: {entry['aday']['cli']} / {entry['aday']['model']} / "
                     f"{entry['aday']['efor']}: {entry['gerekce']} "
                     f"(kip={entry['kota']['kip']}, bağlayıcı={entry['kota']['baglayici']})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Model–efor kadrosu; yalnız öneri üretir.")
    commands = parser.add_subparsers(dest="command", required=True)
    choose = commands.add_parser("secim", help="Bir iş için aday öner")
    choose.add_argument("task_type", choices=TASK_TYPES)
    learn_parser = commands.add_parser("ogren", help="JSONL ölçümlerini tekrarsız öğren")
    learn_parser.add_argument("source", type=Path)
    show = commands.add_parser("goster", help="Bütün iş türleri için seçimi göster")
    for command in (choose, show):
        command.add_argument("--yazan-saglayici", dest="writer_provider")
        command.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "ogren":
            print(json.dumps(learn(args.source), ensure_ascii=False))
            return 0
        config, quotas = load_config(), load_quotas()
        tasks = (args.task_type,) if args.command == "secim" else TASK_TYPES
        results = [select(task, config, quotas, args.writer_provider) for task in tasks]
        if args.json:
            print(json.dumps(results[0] if args.command == "secim" else results,
                             ensure_ascii=False, indent=2, allow_nan=False))
        else:
            print("\n".join(format_result(result) for result in results))
        return 1 if args.command == "secim" and results[0]["aday"] is None else 0
    except (OSError, ValueError, TypeError, OverflowError) as error:
        message = str(error) if isinstance(error, InputError) else type(error).__name__
        if getattr(args, "json", False):
            print(json.dumps({"durum": "hata", "gerekce": message}, ensure_ascii=False))
        else:
            print(f"Hata: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
