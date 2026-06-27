---
name: skill-silo-infra
description: Gestión de Infraestructura y Toolchain Técnico.
tags: [governance, silo, infrastructure, toolchain, whatsapp]
related_skills: [silo-governance, silo-bitacora, skill-silo-personal]
---

# Silo: Infraestructura / Técnico

## 🎯 Contexto
Reglas operativas para el toolchain (Servidores, Notion API, Cloudflare, Hardware y WhatsApp).

## 🛠️ Protocolo de Mantenimiento de WhatsApp
El bridge de WhatsApp depende de `wacli` y un daemon de sync en background.
- **Daemon:** `wacli-sync.service` (systemd).
- **Modo Safe-Sync:** El daemon está configurado con `RestartSec=60` y `StartLimitIntervalSec=300` para prevenir bans por rate-limit (429).
- **Health Check:** Ejecutar `wacli doctor`. Si `CONNECTED` es `false` y `LOCKED` es `true`, el daemon está sincronizando activamente.
- **Recuperación:**
  1. Reiniciar daemon: `systemctl restart wacli-sync`.
  2. Si persisten errores de encriptación: Ejecutar `wacli sync --refresh-contacts`.
  3. Último recurso: Limpiar `~/.wacli` y re-autenticar via `wacli auth`.
- **Seguridad:** El daemon está configurado con `RestartSec=60` y `StartLimitIntervalSec=300` para prevenir loops de retry agresivos que podrían llevar a bans de cuenta.

## 🛠️ Workflow General
1. **Cheat Sheet:** Mantener un "Cheat Sheet" de comandos críticos y puertos.
2. **Quirks de herramientas:** Documentar peculiaridades específicas de herramientas (ej. límites de batch de Notion).
3. **Hardware:** Trackear specs de hardware para propósitos de optimización.

## 📂 Archivos de Referencia
- `references/infra_registry.md` — Registro central de servidores, toolchain, APIs, GitHub, cron jobs, y arquitectura de skills. **Actualizar cuando se consolidé memoria.**

## 🔗 Skills Relacionadas
- `silo-governance` — Gobernanza raíz.
- `silo-bitacora` — Registro de hitos.
- `skill-silo-personal` — Infraestructura de proyectos personales.