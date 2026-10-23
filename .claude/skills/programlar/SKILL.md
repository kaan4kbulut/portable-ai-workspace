---
name: programlar
description: Bu makinede atölyeyle ilgili kurulu program ve servisleri (docker, node, uv, python, llama-server, systemd --user birimleri, tailscale) sürüm ve durumlarıyla listeler; 30-programlar sayfası eksik olanı bildirir. "programlar", "ne kurulu", "servisler çalışıyor mu" dendiğinde kullan.
---
# /programlar — kurulu programlar ve servisler

Salt okunur. Kurulu olmayanı hata sayma, "yok" yaz.

1. Sürümler: `docker --version`, `node --version`, `uv --version`, `python3 --version`, `llama-server --version`, `tailscale version`
   (önce `command -v` ile varlığı sına).
2. Durumlar: `docker ps --format '{{.Names}} {{.Status}}'` (daemon yoksa söyle); `tailscale status` (yalnızca düğüm adları ve çevrimiçi/değil, IP basma);
   `systemctl --user list-units --type=service --no-pager` içinden `20-sistem/servisler/` altındaki birim adlarıyla eşleşenler (active/failed).
3. Eşleştirme: her program için `30-programlar/<ad>/` var mı? Varsa `README.md` yolunu yaz.
4. Tablo: program · sürüm · durum · sayfa. Altında **Eksik sayfalar** (kurulu ama `30-programlar/<ad>/` yok) ve **Servis sapması**
   (`20-sistem/servisler/`'de tanımlı ama çalışmayan birim).
5. Eksik sayfa için `30-programlar/<ad>/README.md` taslağı öner (şablon: `00-cekirdek/sablonlar/belge/bolum-readme.md`); onaysız yazma.
