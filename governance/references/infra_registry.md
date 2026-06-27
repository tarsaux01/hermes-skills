# Registro de Infraestructura — Silo Infra

## 🖥️ Servidores
- **mann** (SSH: `mann`=ubuntu@mann): whatomate / vexa / n8n / rustdesk

## 🔧 Toolchain
- **wacli**: Ejecutable en `/root/go/bin/wacli`
- **wacli-sync.service** (systemd): Daemon de sincronización WhatsApp
  - `RestartSec=60`, `StartLimitIntervalSec=300` (anti-ban rate-limit)
  - Health check: `wacli doctor`
  - Recovery: `systemctl restart wacli-sync` → `wacli sync --refresh-contacts` → limpiar `~/.wacli` + `wacli auth`

## 📦 APIs y Credenciales (`.env`)
- `TOSHL_API_TOKEN` — Toshl finance API (Bearer auth, dos UUIDs concatenados)
- `OLLAMA_API_KEY` — Ollama Cloud
- `TELEGRAM_BOT_TOKEN` — Telegram bot
- `ELEVENLABS_API_KEY` — TTS para audio messages
- `TAVILY_API_KEY` — Web search backend
- `NOTION_API_KEY` — Notion API
- `PERPLEXITY_API_KEY` — Perplexity search
- `XAI_API_KEY` — xAI / Grok

## 📡 Notion
- DB ID: `b99a31f6a17747358dab5181484726ce`
- Parent: `{database_id: "b99a31f6a17747358dab5181484726ce"}`
- Skill `notion` directo, sin pedir credenciales
- Split <2000 chars/bloque
- Ref: `NOTION_PROTOCOL.md`

## 🌐 GitHub
- Repo oficial de skills custom: `https://github.com/tarsaux01/hermes-skills` (público)
- Clone local: `/tmp/hermes-skills-repo/`

## 🤖 Cron Jobs
- `freelance_report.py` (v4) en `/root/.hermes/scripts/` — Freelancer scraping + OCI SMTP + HTML
- Cronjob "do NOT deliver" directive bloquea acceso a email tools en agentes

## 🏗️ Arquitectura de Skills
- **Regla:** NUNCA scripts ad-hoc por query. Arquitectura obligatoria de dos capas:
  - `scripts/<name>_client.py` — Base reutilizable (auth, CRUD, paginación)
  - `scripts/procedures.py` — Funciones de alto nivel
- **Nombres contextuales:** El nombre debe disparar carga por intención
- **Categorías:** `productivity/` = herramientas user-facing, `devops/` = infra, `governance/` = silos

## 📝 Skills Renombrados (Sesión 2026-06-26)
- `recall-ai-automation` → `google-meet-bot` (productivity/)
- `kanban-orchestrator` → `project-manager` (productivity/)
- `silo-manager` → `silo-governance` (raíz de skills)
- `whatsapp-automation` → movido a `productivity/`