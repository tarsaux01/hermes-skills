---
name: silo-governance
description: "The master architectural guide and operational law for Santiago's data silos. This skill governs how information is categorized, stored, and retrieved across the entire ecosystem."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [governance, silos, architecture, knowledge-management]
---

# Silo Governance — The Master Blueprint

This skill is the "Constitutional Law" of the environment. It defines the logical and physical boundaries of information to prevent contamination and ensure high-precision retrieval.

## 1. The Silo Architecture
All information must be mapped to one of the following functional silos:

- **Professional (Hostech):** All business operations, corporate strategy, and Hostech-specific data.
- **Clients:** Freelance and agency client management, project tracking, and deliverables.
- **Personal / R&D:** Personal innovation, hardware/software experiments, and private interests.
- **Research:** Academic knowledge, technical whitepapers, and domain-specific discovery.

### Transversal Silos (Cross-cutting)
Certain data types cut across all silos and have their own governance:
- **Contacts:** The single source of truth for people and relationships.
- **Infra:** Technical toolchain, server configs, and environment details.
- **Bitácora:** Operational logs and daily milestones.
- **Financial Analysis:** Standardized financial evaluation for quotes and loans.
- **Finance Tracker:** Personal expense/income tracking via Toshl API (skill: `finance-tracker`).

## 2. Operational Principles
- **Zero Contamination:** Never mix personal notes into professional silos or vice versa.
- **Source of Truth:** Use the specific governance skill for a silo (e.g., `skill-silo-clients`) to find the definitive file structure and reference documents.
- **Contextual Loading:** This skill should be loaded at the start of every session to ground the agent in the global architecture.

## 3. Skill Architecture & Conventions

### Naming
Santiago's skills must be named **contextually** — the skill name itself should be a natural-language trigger so the agent loads it automatically when the user's intent matches, without the user having to explicitly request it.

- **No technical jargon names:** `kanban-orchestrator` → `project-manager`; `recall-ai-automation` → `google-meet-bot`; `silo-manager` → `silo-governance`.
- **Category placement:** User-facing automation tools (WhatsApp, Meet bots, finance tracking, project management) belong in `productivity/`, not `devops/`. `devops/` is for infrastructure management only.
- **Governance skills** (silo-*) stay in `governance/` except `silo-governance` which lives at the **root** of skills for maximum priority.

### Script Architecture (MANDATORY for all skills with scripts)
**Never generate ad-hoc disposable scripts per query.** Every skill that involves programmatic operations must follow a two-layer architecture:
1. **`scripts/<name>_client.py`** — Reusable base client (auth, CRUD, pagination, error handling). Reads secrets from `.env` directly to bypass the secret redactor.
2. **`scripts/procedures.py`** — High-level functions built on the client. Add new procedures here as they emerge, building a reusable library over time.

### GitHub Backup
All custom skills must be synced to `https://github.com/tarsaux01/hermes-skills` organized by category. After creating or modifying a skill locally, copy it to the repo clone at `/tmp/hermes-skills-repo/` and push.

## 4. Memory Consolidation Protocol (REGLA DE ORO — INAMOVIBLE)

**NUNCA borrar, truncar o perder información por compactación.** Esta es una regla de oro no negociable del ecosistema.

When persistent memory reaches **>95% capacity**, consolidate operational data into silo reference files — **never lose data to compaction**.

### How to consolidate:
1. Identify memory entries that are **operational facts** (server IPs, API tokens locations, tool paths, project status).
2. Map each fact to its corresponding silo:
   - Infra/Toolchain → `skill-silo-infra/references/infra_registry.md`
   - Personal/R&D/Finances → `skill-silo-personal/references/personal_registry.md`
   - Contacts → `skill-silo-contacts/references/contacts_directory.md`
   - Clients → `skill-silo-clients/references/clients_directory.md`
   - Professional → `skill-silo-professional/references/professional_directory.md`
   - Research → `skill-silo-research/references/research_directory.md`
3. Write/update the corresponding reference file with the consolidated info.
4. Remove the entry from persistent memory (using `memory` tool with `action=remove`).
5. Keep in memory only: **user preferences, core protocols, and cross-silo facts**.

### What stays in memory (always):
- User profile facts (name, preferences, communication style)
- Root protocols (load silo-governance, consolidation protocol)
- Cross-cutting facts that don't fit a single silo

### What moves to silos:
- Server configs, API endpoints, tool paths → Infra
- Financial data, Toshl categories, project status → Personal/R&D
- Contact info, family details → Contacts
- Client details, project deliverables → Clients

## 5. Maintenance & Evolution
Changes to the silo structure must be documented here first before being applied to the filesystem or memory.
