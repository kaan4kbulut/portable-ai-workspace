#!/usr/bin/env python3
"""PreToolUse hook: atölye policy guard (Bash | Edit | Write | MultiEdit | NotebookEdit).

Origin: kaan4kbulut/4k-claude .claude/hooks/yikici-koruma.py (2026-10), adapted for the atölye layout.
Rule, not preference: Claude cannot opt out. Runs next to cc-safety-net (generic destructive commands and
secret access, parsed not regex); this hook keeps the atölye-specific rules ("move, don't delete", ANAYASA,
symlinks, writes outside the project) that cc-safety-net allows.

  Edit/Write/MultiEdit/NotebookEdit:
    - target (symlinks resolved) must stay under the project root ($CLAUDE_PROJECT_DIR) or a temp dir
    - 00-cekirdek/ANAYASA.md is always denied (human-only)
    - file names that look like credentials are denied
  Bash, two passes over the command plus everything the shell would execute inside it ($(...), backticks — also inside
  double quotes and unquoted heredocs — and bash/sh/zsh -c payloads):
  1. rule regexes in command position (line start, after ; && || | $( ` or xargs/env/exec/nohup/sudo), also on a
     normalised copy (r''m, r\\m, /bin/rm -> rm);
  2. shlex parse per simple command: cd and NAME=value are tracked, write targets of redirects (incl. 1>, &>), cp, mv,
     install, rsync, tee, truncate, touch, chmod/chown, sed -i/perl -i and interpreter one-liners are resolved;
     ANAYASA, outside-project (temp dirs excepted) and raw devices are denied; unresolved targets ask.
  Internal error => ask (never a silent allow). Rule regexes:
    deny: rm -r/-R/--recursive, find -delete / -exec rm, shutil.rmtree / os.remove scripts,
          git reset --hard, git push --force / -f / +refspec, git clean -f, git checkout -- .,
          DROP/TRUNCATE, chmod 777, curl|sh, mkfs, dd if=, ln -s inside the repo,
          reading credential files, claude setup-token, shell writes to ANAYASA.md,
          redirects outside the project and temp dirs (/dev/null, /dev/stdout, /dev/stderr excepted)
    ask:  single-file rm, rm -f, sudo
  False-positive guards: git commit -m messages, cat/tee/git heredoc bodies and grep/rg patterns are data, not commands;
  '>' inside quotes is not a redirect.
Output: hookSpecificOutput.permissionDecision deny|ask + reason; silent exit 0 when allowed.
"""
import json
import os
import re
import shlex
import sys

ANAYASA = "00-cekirdek/ANAYASA.md"
KIMLIK_ADLARI = re.compile(r"(\.credentials(\.json)?$|(^|/)auth\.json$|token|secret)", re.I)
# no tempfile.gettempdir(): it probes writability and crashes on read-only filesystems
GECICI = tuple(sorted({os.path.realpath(p) + os.sep for p in ("/tmp", os.environ.get("TMPDIR") or "/tmp")}))
AYGITLAR = ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty")

# Command position: line start or after a separator/wrapper.
KK = (r"(?:^|[;&|(`\n{]|\$\()\s*(?:(?:xargs|env|exec|nohup|time|command|builtin|sudo|do|then|else|elif|if|while|until|!|"
      r"timeout\s+\S+)\s+(?:-\S+\s+)*)*")
# bash -c "payload" / sh -c 'payload'
IC_KABUK = re.compile(r"\b(?:ba|z|da)?sh\s+(?:-[a-zA-Z]+\s+)*-[a-zA-Z]*c\s+(?:\"((?:[^\"\\]|\\.)*)\"|'([^']*)')")

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
    (KK + r"ln\s+(?:\S+\s+)*?(-[a-zA-Z]*s[a-zA-Z]*|--symbolic)\b", "symlink yasak (ANAYASA 2.2); kur.sh --genel dışında bağlantı kurulmaz"),
    (KK + r"claude\s+setup-token", "claude setup-token yasak (AGENTS.md Kesin kural 1)"),
    (r"(\.claude/\.credentials\.json|\.codex/auth\.json|\.gemini/[^\s]*(auth|oauth|cred)|\.config/gh/hosts\.yml)",
     "kimlik dosyasına dokunma yasak; giriş durumu için aracın kendi komutu"),
]

SOR = [
    (KK + r"sudo\b", "sudo sahibinin onayını ister"),
    (KK + r"rm\s+(?!-)\S", "tek dosya silme onay ister; tercih: 60-arsiv/'e taşı"),
    (KK + r"rm\s+-[a-zA-Z]*f[a-zA-Z]*\s", "rm -f onay ister; tercih: 60-arsiv/'e taşı"),
]

KORUNAN = re.compile(r"ANAYASA\.md")
# interpreter one-liners that write files (used only together with a protected path in the same payload)
YORUMLAYICI_YAZAR = re.compile(r"(write_text|write_bytes|open\([^)]*['\"][wax+]|os\.(replace|rename)|shutil\.|writeFile|appendFile|"
                               r"fs\.\w*(write|copy|rename)|File\.write|IO\.write|truncate|chmod)")
SARMALAYICI = {"sudo", "env", "nohup", "time", "command", "builtin", "exec", "nice", "stdbuf", "doas"}
KABUK_SOZCUK = {"do", "then", "else", "elif", "if", "while", "until", "!", "{", "}"}
AYIRAC = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}
YONLENDIRME = {">", ">>", ">|", "&>", "&>>"}


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


def ic_komutlari_ekle(tarama):
    """Append bash/sh -c payloads (up to 3 levels) so they are scanned in command position."""
    parcalar, simdiki = [tarama], tarama
    for _ in range(3):
        ic = ["\n".join(g for g in m if g) for m in IC_KABUK.findall(simdiki)]
        if not ic:
            break
        simdiki = "\n".join(veri_kisimlarini_cikar(p.replace('\\"', '"')) for p in ic)
        parcalar.append(simdiki)
    return "\n".join(parcalar)


def komut_ikameleri(komut):
    """Bodies of $(...) and `...` that the shell would execute (also inside double quotes and unquoted heredocs).

    Quoted-heredoc bodies and single-quoted strings are not expanded by the shell, so they are dropped first.
    """
    k = re.sub(r"<<-?\s*(['\"])(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?=\n|$|\))", "<<Q", komut, flags=re.S)
    k = re.sub(r"'[^']*'", "''", k)
    sonuc, i = [], 0
    while True:
        i = k.find("$(", i)
        if i < 0:
            break
        derinlik, j = 1, i + 2
        while j < len(k) and derinlik:
            derinlik += {"(": 1, ")": -1}.get(k[j], 0)
            j += 1
        sonuc.append(k[i + 2:j - 1])
        i += 2
    sonuc += re.findall(r"`([^`]*)`", k)
    return [veri_kisimlarini_cikar(s) for s in sonuc if s.strip()]


def normallestir(s):
    """Defeat word tricks for rule matching only: r''m, r\\m, /bin/rm -> rm."""
    s = re.sub(r"''|\"\"|\\(?=[a-zA-Z])", "", s)
    return re.sub(r"(^|[\s;&|(`]|\$\()(?:/[\w.+-]+)+/(?=[a-z][\w.+-]*(?:\s|$))", r"\1", s, flags=re.M)


def mutlak_yol(hedef, cwd):
    hedef = os.path.expanduser(hedef)
    return os.path.realpath(hedef if os.path.isabs(hedef) else os.path.join(cwd, hedef))


def degisken_coz(metin, degiskenler):
    return re.sub(r"\$\{?(\w+)\}?", lambda m: degiskenler.get(m.group(1), m.group(0)), metin)


def yazma_hedefi_denetle(kok, cwd, hedef, nasil, degiskenler=None):
    """Deny when a shell write target is ANAYASA, outside the project (temp dirs excepted) or a raw device."""
    if degiskenler is not None:
        hedef = degisken_coz(hedef, degiskenler)
    if not hedef or hedef.startswith("&") or hedef in AYGITLAR or re.match(r"/dev/fd/\d+$", hedef):
        return
    if "$" in hedef or "`" in hedef:
        karar("ask", f"yazma hedefi çözülemedi ({nasil}): {hedef}; elle onay")
    mutlak = mutlak_yol(hedef, cwd)
    if os.path.relpath(mutlak, os.path.realpath(kok)).replace(os.sep, "/") == ANAYASA:
        karar("deny", f"ANAYASA.md kabukla değiştirilmez (yalnız insan) — {nasil}: {hedef}")
    if not kok_icinde(kok, mutlak) and not mutlak.startswith(GECICI):
        karar("deny", f"proje dışına yazma ({nasil}): {hedef}")


def tirnaksiz(jeton):
    """Unquote a non-POSIX shlex token; a quoted operator (">", ";") is tagged with \\0 so it is never an operator."""
    deger = re.sub(r"^(['\"])(.*)\1$", r"\2", jeton, flags=re.S)
    if deger != jeton and deger in YONLENDIRME | AYIRAC | {">&", "<", "<<", "<&"}:
        return "\0" + deger
    return deger


def parcalar(metin):
    """Split shell text into simple commands (lists of words), honouring quotes. None when it cannot be parsed."""
    sonuc = []
    for satir in metin.split("\n"):
        # posix=False keeps the quotes, so a quoted '>' stays distinguishable from a real redirect
        lx = shlex.shlex(satir, posix=False, punctuation_chars=";&|()<>")
        lx.whitespace_split = True
        lx.commenters = ""
        try:
            jetonlar = [tirnaksiz(j) for j in lx]
        except ValueError:
            return None
        simdiki = []
        for j in jetonlar:
            if j in AYIRAC:
                if simdiki:
                    sonuc.append(simdiki)
                simdiki = []
            else:
                simdiki.append(j)
        if simdiki:
            sonuc.append(simdiki)
    return sonuc


def secenek_disi(argumanlar):
    return [a for a in argumanlar if not a.startswith("-")]


def parca_denetimi(kok, cwd, metin):
    """Per simple command: track cd, check every write target (redirects, cp/mv/install/tee/sed -i/chmod, interpreters)."""
    # heredoc bodies are stdin data for the command, not shell commands
    metin = re.sub(r"(<<-?\s*['\"]?(\w+)['\"]?[^\n]*)\n.*?\n\s*\2\s*(?=\n|$)", r"\1", metin, flags=re.S)
    liste = parcalar(metin)
    if liste is None:
        karar("ask", "komut ayrıştırılamadı (kapanmamış tırnak?); elle onay")
    degiskenler = {"HOME": os.path.expanduser("~"), "PWD": cwd}
    for kelimeler in liste:
        k = list(kelimeler)
        # NAME=value assignments (alone or as command prefix) are remembered for later targets
        for j in k:
            m = re.match(r"^(\w+)=(.*)$", j)
            if not m:
                break
            degiskenler[m.group(1)] = os.path.expanduser(degisken_coz(m.group(2), degiskenler))
        degiskenler["PWD"] = cwd
        hedef_denetle = lambda h, nasil: yazma_hedefi_denetle(kok, cwd, h, nasil, degiskenler)  # noqa: E731
        # redirects anywhere in the simple command; '1>' arrives as '1' + '>'
        for i, j in enumerate(k):
            if j in YONLENDIRME and i + 1 < len(k):
                hedef_denetle(k[i + 1], "yönlendirme")
            # '>& file' writes to a file; '>&2', '>&-' only duplicate/close descriptors
            if j == ">&" and i + 1 < len(k) and not re.match(r"^(\d+|-)$", k[i + 1]):
                hedef_denetle(k[i + 1], "yönlendirme")
        k = [j for i, j in enumerate(k) if j not in YONLENDIRME and not (i and k[i - 1] in YONLENDIRME | {">&"})
             and not (j.isdigit() and i + 1 < len(k) and k[i + 1] in YONLENDIRME) and j not in ("<", "<<", ">&", "<&")]
        k = [j.lstrip("\0") for j in k]
        while k and (k[0] in SARMALAYICI or k[0] in KABUK_SOZCUK or re.match(r"^\w+=", k[0])
                     or (k[0] == "timeout" and len(k) > 1)):
            k = k[2:] if k[0] == "timeout" else k[1:]
            while k and k[0].startswith("-"):
                k = k[1:]
        if not k:
            continue
        ad, arg = os.path.basename(re.sub(r"''|\"\"", "", k[0])), k[1:]
        duz = secenek_disi(arg)
        if ad == "cd":
            if duz and duz[0] != "-":
                cwd = mutlak_yol(degisken_coz(duz[0], degiskenler), cwd)
            continue
        if ad in ("cp", "install", "rsync", "scp", "mv"):
            t = next((arg[i + 1] for i, a in enumerate(arg[:-1]) if a in ("-t", "--target-directory")), None)
            t = t or next((a.split("=", 1)[1] for a in arg if a.startswith("--target-directory=")), None)
            kaynaklar = duz if t else duz[:-1]
            hedef = t or (duz[-1] if len(duz) >= 2 else None)
            if hedef:
                hedef_denetle(hedef, ad)
                # a directory target really writes <dir>/<basename of each source>
                hm = mutlak_yol(degisken_coz(hedef, degiskenler), cwd)
                if os.path.isdir(hm) or hedef.endswith("/"):
                    for s in kaynaklar:
                        hedef_denetle(os.path.join(hedef, os.path.basename(s.rstrip("/"))), ad)
            if ad == "mv":
                for a in kaynaklar:
                    hedef_denetle(a, "mv (kaynak)")
        elif ad == "git":
            g = list(arg)
            while len(g) >= 2 and g[0] in ("-C", "-c", "--git-dir", "--work-tree"):
                g = g[2:]
            if g and g[0] in ("restore", "checkout", "mv", "rm", "apply", "stash") and any(KORUNAN.search(a) for a in g):
                karar("deny", f"ANAYASA.md git ile değiştirilmez (yalnız insan) — git {g[0]}")
        elif ad in ("curl", "wget"):
            for i, a in enumerate(arg[:-1]):
                if a in ("-o", "--output", "-O", "--output-document"):
                    hedef_denetle(arg[i + 1], ad)
            for a in arg:
                if a.startswith(("--output=", "--output-document=")):
                    hedef_denetle(a.split("=", 1)[1], ad)
        elif ad in ("tee", "truncate", "touch", "chmod", "chown", "chattr", "chgrp"):
            hedefler = duz[1:] if ad in ("chmod", "chown", "chgrp", "chattr") else duz
            for a in hedefler:
                hedef_denetle(a, ad)
        elif ad in ("sed", "perl") and any(re.match(r"^-[a-zA-Z]*i", a) or a.startswith("--in-place") for a in arg):
            betik_var = any(a in ("-e", "--expression", "-f") for a in arg)
            for a in (duz if betik_var else duz[1:]):
                hedef_denetle(a, f"{ad} -i")
        elif re.match(r"^(python[\d.]*|node|perl|ruby|php|deno|bun)$", ad):
            yuk = " ".join(arg)
            if KORUNAN.search(yuk) and YORUMLAYICI_YAZAR.search(yuk):
                karar("deny", f"ANAYASA.md yorumlayıcıyla değiştirilmez (yalnız insan) — {ad}")
            if YORUMLAYICI_YAZAR.search(yuk):
                for p in re.findall(r"['\"]((?:/|~/)[^'\"]+)['\"]", yuk):
                    m = mutlak_yol(p, cwd)
                    if not kok_icinde(kok, m) and not m.startswith(GECICI) and m not in AYGITLAR:
                        karar("ask", f"yorumlayıcı proje dışına yazabilir ({ad}): {p}; elle onay")


def kok_icinde(kok, yol):
    kok_m = os.path.realpath(kok)
    return yol == kok_m or yol.startswith(kok_m + os.sep)


def yol_izinli(kok, hedef):
    if not hedef:
        return True, ""
    mutlak = os.path.realpath(hedef if os.path.isabs(hedef) else os.path.join(kok, hedef))
    if not kok_icinde(kok, mutlak):
        if mutlak.startswith(GECICI):
            return True, ""
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
    try:
        denetle(girdi)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001  fail safe: an internal error must never mean "allow"
        karar("ask", f"hook iç hatası ({type(e).__name__}: {e}); elle onay")


def denetle(girdi):
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
    # data parts (commit messages, quoted heredocs, grep patterns) are stripped, but anything the shell would
    # execute inside them ($(...), backticks, bash -c payloads) is appended and scanned as a command
    tarama = ic_komutlari_ekle("\n".join([veri_kisimlarini_cikar(komut)] + komut_ikameleri(komut)))
    kural_metni = tarama + "\n" + normallestir(tarama)
    kisa = komut[:160]
    for kalip, neden in REDDET:
        if re.search(kalip, kural_metni, re.I | re.M):
            karar("deny", f"{neden} — komut: {kisa}")
    if re.search(r"\b(python[\d.]*|node|perl|ruby|php|deno|bun)\b", komut) and KORUNAN.search(komut) \
            and YORUMLAYICI_YAZAR.search(komut):
        karar("deny", f"ANAYASA.md yorumlayıcıyla değiştirilmez (yalnız insan) — komut: {kisa}")
    parca_denetimi(kok, cwd, tarama)
    for kalip, neden in SOR:
        if re.search(kalip, kural_metni, re.I | re.M):
            karar("ask", f"{neden} — komut: {kisa}")
    sys.exit(0)


if __name__ == "__main__":
    main()
