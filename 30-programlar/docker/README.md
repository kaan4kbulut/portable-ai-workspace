---
katman: programlar
surum: 29.1.3
son_kontrol: 2026-10-23
kaynaklar: [https://docs.docker.com, https://github.com/moby/moby]
baglar: [../README.md, ../../10-donanim/monster/README.md, ../yerel-modeller/README.md]
---

# Docker (`docker`)

## Nedir
Konteyner çalışma zamanı (`Docker version 29.1.3, build 29.1.3-0ubuntu4.1`) ve `docker compose` orkestrasyon aracıdır.
Atölyede yerel model sunucusu (`llama.cpp` CUDA imajı) ve yalıtılmış servis konteynerlerini çalıştırmak için kullanılır.

## Atölyedeki rolü
- **Yerel model ve servis taşıyıcısı:** MONSTER üzerinde GPU hızlandırmalı `llama-server` (`server-cuda` Docker imajı) çalıştırarak basit görevleri bulut kotası harcamadan yerel modele yönlendirir (`00-cekirdek/AGENTS.md`, `60-hafiza/kararlar/KARARLAR.md`).
- `30-programlar/docker/compose/` altında servis tanımlarını barındırır; veri hacimleri ve imajlar makine-yerel kalır.

## Kurulum ve giriş
- Denetim betiği: `bash 20-sistem/kurulum/araclar/docker.sh` (Docker kurulumu root/apt gerektirdiği için yalnızca kurulu olup olmadığını raporlar, otomatik sudo çalıştırmaz).
- Makine kurulumu (sudo gerektirir, `10-donanim/<makine>/` kapsamında elle):
  `sudo apt-get install -y docker.io docker-compose-v2 && sudo usermod -aG docker $USER`
- Kayıt defteri girişi gerekirse yalnızca kendi komutuyla yapılır: `docker login` (çıkış: `docker logout`).

## Etkileşimsiz çağırma
`docker --help` ile bu makinede doğrulanan komut ve bayraklar:
```bash
docker ps --format json
docker compose -f 30-programlar/docker/compose/llama-server.yml up -d
docker compose -f 30-programlar/docker/compose/llama-server.yml ps
docker stats --no-stream
```
- Seçenekler: `--config <dizin>`, `-c`/`--context <ad>`, `-H`/`--host <soket>`, `-l`/`--log-level <debug|info|warn|error|fatal>`, `docker run -d --rm --gpus all`, `docker compose -f <dosya> up -d / down / logs`.

## Okuduğu dosyalar
- **Daemon ayarları:** `/etc/docker/daemon.json` (sistem geneli; NVIDIA runtime, log-driver, depolama ayarları) veya rootless kipte `~/.config/docker/daemon.json`.
- **İstemci ayarları ve kimlik (depoya girmez):** `~/.docker/config.json` (registry kimlik bilgileri, CLI eklentileri, vekil sunucu ayarları).
- **Atölye Compose dosyaları:** `30-programlar/docker/compose/*.yml` (veya yeni katmanda `30-programlar/docker/compose/*.yml`).

## Dikkat
- **Yetki ve güvenlik sınırı:** `docker` grubuna üye olmak root eşdeğeri yetki verir. Bu nedenle LENOVO sunucusunda ajanlar `docker` yetkisi olmayan ayrı `ajan` kullanıcısında çalışır (`60-hafiza/kararlar/KARARLAR.md`).
- **Ağ yalıtımı:** Konteyner portları (`-p 127.0.0.1:8080:8080` gibi) yalnızca localhost veya `tailscale serve` ile tailnet'e bağlanır; `0.0.0.0` ile dış ağa/internete hiçbir servis açılmaz.
- **Yıkıcı komutlar:** `docker system prune -a --volumes` veya veri silen komutlar kullanıcı onayı olmadan çalıştırılmaz.

## Eksikler
- MONSTER üzerinde `nvidia-container-toolkit` kurulumu ve `docker run --gpus all` doğrulaması henüz yapılmadı (`00-cekirdek/PLAN.md` Altyapı 3).
- `llama.cpp` `server-cuda` için `compose/llama-server.yml` dosyası Altyapı 3 aşamasında yazılacak.
