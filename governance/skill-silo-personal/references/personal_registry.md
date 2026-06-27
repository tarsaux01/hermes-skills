# Registro Personal / R&D — Silo Personal

## 💰 Finanzas Personales (Toshl)
- **Skill:** `finance-tracker` en `productivity/`
- **API:** `https://api.toshl.com/` (sin `/v1` prefix)
- **Auth:** `Authorization: Bearer <token>`
- **Params:** PLURALES (`categories`, `tags`, `accounts`) — los singulares NO funcionan
- **Categorías clave:**
  - `74544372` = Servicios IA (OpenAI, ElevenLabs, Copilot, Perplexity, Grok, Ollama Cloud, Spellar AI, FireFlies)
  - `63328388` = Servicios Digitales (Netflix, Spotify, Google Cloud, Digital Ocean, etc.)
  - `63328374` = Alimentación
  - `63328377` = Emergente/No Planeado
- **Mapeo local:** `productivity/finance-tracker/references/toshl_map.json` (37 cats, 30 accounts, 195 tags)
- **Scripts:** `toshl_client.py` (base) + `procedures.py` (procedimientos)
- **Quirks documentados:** `references/toshl-api-quirks.md`

## 📊 Reportes Generados
- **Junio 2026:** Ingreso $106,246.85 MXN, Gasto $94,653.95 MXN, Balance +$11,592.90 MXN
- **Split Digital → IA:** 63 entradas movidas (17 IA + 40 Copilot + 6 extras multi-tag)
- **Entradas "L":** 192 entradas (ago 2023 → dic 2026), $77,941.08 MXN total

## 🎯 Proyectos R&D
- `local-agent-optimization` — Optimización de hardware/software para agentes locales
- Modelo activo: `glm-5.2` via `ollama-cloud`

## 👤 Identidad del Agente
- **Nombre:** TARS
- **Personalidad:** Friendly, efficient, witty, tech-savvy, mediator
- **Birthdate:** March 1st, 2026