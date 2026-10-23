---
paths:
  - "**/*.sh"
  - "**/*.py"
---
# Betik kuralları (atölye)

- Bash: `#!/usr/bin/env bash` + `set -euo pipefail`; ilk yorum satırı amaç ve kullanım (İngilizce).
- Kendi konumunu `$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)` ile bul; atölye kökünü oradan göreli türet. Mutlak yol yazma.
- Başka betiği `bash "$DIR/x.sh"` ile çağır; `./x.sh` değil (çalıştırma bitine güven yok, exFAT).
- Python hook'ları: yalnızca standart kütüphane; `sys.stdin` JSON okur; kök `os.environ["CLAUDE_PROJECT_DIR"]`; engel = stderr + `sys.exit(2)`.
- `jq` gibi dış araçlara bağımlı olma; bash + python3 + git + coreutils yeter.
- Yeniden çalıştırılabilir (idempotent) ol: var olanı atla, üzerine yazmadan önce `.yedek-<zaman>` al.
- Kimlik dosyası okuma/yazma; giriş durumu yalnızca aracın kendi komutuyla (`gh auth status`, `codex login status`, `opencode auth list`).
- Çıkış kodları: 0 temiz, 1 uyarı, 2 hata. Çıktı tek biçim: `[HATA|UYARI|OK] kural · yol · öneri`.
