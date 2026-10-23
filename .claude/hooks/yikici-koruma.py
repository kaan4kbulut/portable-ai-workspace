#!/usr/bin/env python3
"""PreToolUse hook: destructive-action guard (Bash | Edit | Write | MultiEdit | NotebookEdit).

Origin: kaan4kbulut/4k-claude .claude/hooks/yikici-koruma.py (2026-10), adapted for the atölye layout.
Rule, not preference: Claude cannot opt out.

  Edit/Write/MultiEdit/NotebookEdit:
    - target (symlinks resolved) must stay under the project root ($CLAUDE_PROJECT_DIR)
    - 00-cekirdek/ANAYASA.md is always denied (human-only)
    - file names that look like credentials are denied
  Bash, in command position (line start, after ; && || | $( ` or xargs/env/exec/nohup):
    deny: rm -r/-R/--recursive, find -delete / -exec rm, shutil.rmtree / os.remove scripts,
          git reset --hard, git push --force / -f / +refspec, git clean -f, git checkout -- .,
          DROP/TRUNCATE, chmod 777, curl|sh, mkfs, dd if=, ln -s inside the repo,
          reading credential files, claude setup-token, shell writes to ANAYASA.md,
          redirects outside the project (/dev/null, /dev/stdout, /dev/stderr excepted)
    ask:  single-file rm, rm -f, sudo
  False-positive guards: git commit -m messages, cat/tee/git heredoc bodies and grep/rg patterns are data, not commands.
Output: hookSpecificOutput.permissionDecision deny|ask + reason; silent exit 0 when allowed.
"""
import json
import os
import re
import sys

ANAYASA = "00-cekirdek/ANAYASA.md"
KIMLIK_ADLARI = re.compile(r"(\.credentials(\.json)?$|(^|/)auth\.json$|token|secret)", re.I)

# Command position: line start or after a separator/wrapper.
KK = r"(?:^|[;&|(`\n]|\$\()\s*(?:(?:xargs|env|exec|nohup|time|command|builtin|timeout\s+\S+)\s+(?:-\S+\s+)*)*"

REDDET = [
    (KK + r"rm\s+(?:\S+\s+)*?(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)\b", "rm -r yasak; 60-arsiv/'e taşı (ANAYASA 6.4)"),
    (r"\bfind\b[^;&|]*\s(-delete\b|-exec(dir)?\s+rm\b)", "find -delete / -exec rm yasak; arşive taşı"),
    (r"\b(shutil\.rmtree|os\.remove|os\.unlink|os\.rmdir|fs\.rm(Sync)?\(|fs\.unlink)", "betikle silme yasak; arşive taşı"),
    (KK + r"git\s+(?:-[cC]\s+\S+\s+)*reset\s+--hard", "git reset --hard yasak"),
    (KK + r"git\s+(?:-[cC]\s+\S+\s+)*push\b[^;&|]*(--force|--force-with-lease|\s-[a-zA-Z]*f\b|\s\+\S+)", "force push yasak"),
    (KK + r"git\s+(?:-[cC]\s+\S+\s+)*clean\s+-[a-zA-Z]*f", "git clean -f yasak"),
    (KK + r"git\s+(?:-[cC]\s+\S+\s+)*checkout\s+(\S+\s+)?--\s+\.", "git checkout -- . yasak"),
    (r"\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b", "DROP/TRUNCATE yasak"),
    (KK + r"chmod\s+(-R\s+)?0?777\b", "chmod 777 yasak"),
    (r"\b(curl|wget)\b[^|;&]*\|\s*(sudo\s+)?(sh|bash|zsh|fish|python3?)\b", "indir-ve-çalıştır yasak; önce dosyaya indir, oku"),
    (KK + r"(mkfs(\.\w+)?|dd\s+if=)", "disk işlemleri yasak"),
    (KK + r"ln\s+-[a-zA-Z]*s", "symlink yasak (ANAYASA 2.2); kur.sh --genel dışında bağlantı kurulmaz"),
    (KK + r"claude\s+setup-token", "claude setup-token yasak (AGENTS.md Kesin kural 1)"),
    (r"(\.claude/\.credentials\.json|\.codex/auth\.json|\.gemini/[^\s]*(auth|oauth|cred)|\.config/gh/hosts\.yml)",
     "kimlik dosyasına dokunma yasak; giriş durumu için aracın kendi komutu"),
]

SOR = [
    (KK + r"sudo\b", "sudo sahibinin onayını ister"),
    (KK + r"rm\s+(?!-)\S", "tek dosya silme onay ister; tercih: 60-arsiv/'e taşı"),
    (KK + r"rm\s+-[a-zA-Z]*f[a-zA-Z]*\s", "rm -f onay ister; tercih: 60-arsiv/'e taşı"),
]

KORUNAN = r"ANAYASA\.md"
YAZAN = r"(>{1,2}|\btee\b|\bsed\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*i|\bperl\s+(-\S+\s+)*-[a-zA-Z]*i|\bcp\b|\bmv\b|\btruncate\b|\binstall\b|open\([^)]*['\"][wa])"


def karar(tur, neden):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": tur,
            "permissionDecisionReason": f"yikici-koruma: {neden}",
        }
    }, ensure_ascii=False))
    sys.exit(0)


def veri_kisimlarini_cikar(komut):
    """Strip commit messages, cat/tee/git heredoc bodies and grep patterns (data, not commands)."""
    k = re.sub(r"(\bgit\b[^;&|\n]*\bcommit\b[^;&|\n]*?)(-m|--message)(=|\s+)(\"(?:[^\"\\]|\\.)*\"|'[^']*'|\$\(cat\s+<<.*?\))",
               r"\1\2 MESAJ", komut, flags=re.S)

    def heredoc(m):
        return m.group(1) + " HEREDOC\n" if re.search(r"\b(cat|tee|git)\b", m.group(1)) else m.group(0)

    k = re.sub(r"([^\n]*<<-?\s*['\"]?(\w+)['\"]?[^\n]*)\n.*?\n\s*\2\s*(?=\n|$)", heredoc, k, flags=re.S)
    k = re.sub(r"(\b(?:grep|rg|egrep|fgrep)\b(?:\s+-\S+)*)\s+(\"[^\"]*\"|'[^']*'|\S+)", r"\1 DESEN", k)
    return k


def kok_icinde(kok, yol):
    kok_m = os.path.realpath(kok)
    return yol == kok_m or yol.startswith(kok_m + os.sep)


def yol_izinli(kok, hedef):
    if not hedef:
        return True, ""
    mutlak = os.path.realpath(hedef if os.path.isabs(hedef) else os.path.join(kok, hedef))
    if not kok_icinde(kok, mutlak):
        return False, f"proje kökü dışına yazma: {hedef}"
    goreli = os.path.relpath(mutlak, os.path.realpath(kok)).replace(os.sep, "/")
    if goreli == ANAYASA:
        return False, "ANAYASA.md yalnız insan tarafından düzenlenir (AGENTS.md Kesin kural 5)"
    if KIMLIK_ADLARI.search(os.path.basename(goreli)):
        return False, f"kimlik/sır ima eden dosya adı yasak: {goreli} (ANAYASA 3.5)"
    return True, ""


def main():
    try:
        girdi = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        sys.exit(0)
    kok = os.environ.get("CLAUDE_PROJECT_DIR") or girdi.get("cwd") or os.getcwd()
    cwd = girdi.get("cwd") or kok
    arac = girdi.get("tool_name", "")
    ti = girdi.get("tool_input", {}) or {}

    if arac in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        hedef = ti.get("file_path") or ti.get("notebook_path") or ti.get("path") or ""
        ok, neden = yol_izinli(kok, hedef)
        if not ok:
            karar("deny", neden)
        sys.exit(0)

    if arac != "Bash":
        sys.exit(0)

    komut = ti.get("command", "") or ""
    tarama = veri_kisimlarini_cikar(komut)
    kisa = komut[:160]
    for kalip, neden in REDDET:
        if re.search(kalip, tarama, re.I | re.M):
            karar("deny", f"{neden} — komut: {kisa}")
    if re.search(KORUNAN, tarama) and re.search(YAZAN, tarama):
        for parca in re.split(r"[;&|\n]+", tarama):
            if re.search(KORUNAN, parca) and re.search(YAZAN, parca):
                karar("deny", f"ANAYASA.md kabukla değiştirilmez (yalnız insan) — komut: {kisa}")
    for m in re.finditer(r"(?<![<>0-9&])>{1,2}\s*([^\s;&|<>()]+)", tarama):
        hedef = m.group(1).strip("'\"")
        if hedef.startswith("&") or hedef in ("/dev/null", "/dev/stdout", "/dev/stderr"):
            continue
        mutlak = os.path.realpath(os.path.expanduser(hedef) if hedef.startswith(("/", "~")) else os.path.join(cwd, hedef))
        if not kok_icinde(kok, mutlak) and not mutlak.startswith(("/tmp/", "/dev/")):
            karar("deny", f"proje dışına yönlendirme: {hedef}")
    for kalip, neden in SOR:
        if re.search(kalip, tarama, re.I | re.M):
            karar("ask", f"{neden} — komut: {kisa}")
    sys.exit(0)


if __name__ == "__main__":
    main()
