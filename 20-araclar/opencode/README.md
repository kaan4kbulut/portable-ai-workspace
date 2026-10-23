# 20-araclar/opencode

Proje içinde kök `opencode.json` `instructions` ile `00-cekirdek/AGENTS.md` ve kök `AGENTS.md`'yi yükler.
Global: `kur.sh --genel` ile `~/.config/opencode/AGENTS.md` → `00-cekirdek/AGENTS.md`,
`~/.config/opencode/opencode.json` → `genel/opencode.json` (Aşama 2'de mevcut dosyadan alınır; izin listesi + review ajanı).
Giriş: `opencode auth login` / `opencode auth list`. Makine-yerel: `~/.config/opencode/service.json`, `~/.local/share/opencode/`.
