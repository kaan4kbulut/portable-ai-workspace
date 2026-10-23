# onarimlar/ — yeniden kullanılabilir onarım reçeteleri

Bakımcı ajanın (ya da insanın) bir kez elle çözdüğü, tekrarlanabilir her sorun burada bir betik olur; ikinci kez betik
çalıştırılır. Her betik: `#!/usr/bin/env bash`, `set -euo pipefail`, ilk yorum satırında belirti + ne yaptığı, idempotent,
`bash onarimlar/<ad>.sh` ile çağrılır. `bilinen-sorunlar.md` tablosunun "betik" sütunu buraya işaret eder.

**Girer:** onarım betikleri. **Girmez:** kurulum (→ `../../kurulum/`), sudo gerektiren adımlar (→ `../../cihazlar/<makine>/sudo-*.sh`).
