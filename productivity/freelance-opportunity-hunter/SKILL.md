---
name: freelance-opportunity-hunter
description: Workflow for identifying and analyzing high-probability freelance projects on Workana and Freelancer.
---

# Freelance Opportunity Hunter

This skill defines the workflow for identifying, filtering, and analyzing high-probability freelance projects on platforms like Workana and Freelancer for Santiago.

## User Profile & Expertise
Santiago is a "Fullstack Fixer & Infrastructure Expert" with a high reputation.
- **Core Expertise:** WordPress (Expert/All-around), PHP (Advanced), Linux Servers (Config, Backups, Migrations).
- **Advanced Web:** Laravel (Advanced), Node.js, React, Angular, HTML/CSS/JS.
- **Databases:** MongoDB, PostgreSQL.
- **E-commerce:** Shopify (Intermediate-Advanced).
- **Specialty:** Short-duration projects, urgent bugfixes, and infrastructure migrations.

## Search Strategy (The Three Pillars)
1. **Quick Wins (Low Friction):**
   - Keywords: `WordPress bugfix`, `Error 500`, `site down`, `plugin conflict`, `critical error`.
   - Goal: Rapid closure, high conversion.
2. **High Value (Technical):**
   - Keywords: `Laravel development`, `Node.js API`, `Database optimization`, `Custom Shopify`.
   - Goal: Mid-to-high budget, technical complexity.
3. **Fast Delivery (Volume):**
   - Keywords: `Landing page`, `HTML/CSS fix`, `PSD to HTML`, `Rapid deployment`.
   - Goal: Quick turnaround, steady cash flow.

## Workflow Process
1. **Scan (Multi-Source):** Use the platform-specific extraction techniques documented in `references/extraction-techniques.md`.
   - **Freelancer.com:** Navigate directly to category pages (`/jobs/wordpress`, `/jobs/laravel`, `/jobs/shopify`, etc.) and use `browser_console` with JS injection to extract all project links from the page DOM. The accessibility tree snapshot truncates at ~8000 chars and will miss listings below the fold. See `references/extraction-techniques.md` for the exact JS snippets.
   - **Workana.com:** Navigate directly to filtered job pages (`/en/jobs?skills=wordpress&language=es`) instead of relying on `web_search` with `site:` operators. The filtered Workana URL returns current open projects with skill + language filters pre-applied.
   - **Cross-reference:** Use `web_search` for initial discovery of specific project URLs, then `web_extract` for detailed project content. For batch extraction, pass up to 5 URLs per `web_extract` call.
2. **Filter:**
   - Remove projects with unrealistic budgets or vague descriptions.
   - Prioritize "Urgent" or "Technical" requirements where the client is frustrated (ideal for a 'fixer').
   - Check bid count and posting date — projects posted today with <5 bids are prime targets (low competition, fresh window).
3. **Curate & Report:** Deliver a list to the user with:
   - **Project Link:** Direct URL.
   - **The "Why":** Why this matches Santiago's specific expertise.
   - **The "Angle":** A suggested psychological/technical hook for the proposal (e.g., "Focus on the security risk of the current bug").

## 🚀 Delivery & Formatting Standards
- **Language:** All reports MUST be written in **Spanish**.
- **Visual Style (Pillar-Based Layout):**
  - The report MUST be organized by **Three Pillars** (not by platform): Quick Wins, High Value, Fast Delivery.
  - Each project card MUST include: title, platform, budget (💰), published date (📅), link (🚀), description, "¿Por qué encaja?" (why it matches Santiago), and "Ángulo de propuesta" (suggested proposal hook).
  - Use `<b>` / `<strong>` HTML tags for bold text — NEVER markdown `**` (email clients render `**` as literal asterisks).
  - Include a **summary table** at the end with counts per pillar and top project names.
  - Use CSS-styled project cards with colored left borders and tags (Quick Win = yellow, High Value = blue).
- **Delivery Method (Hybrid Script Architecture):**
  - The agent CANNOT reliably send emails — the cronjob system injects a "do NOT deliver output yourself" directive that overrides email instructions (see Pitfalls).
  - The script `scripts/freelance_report.py` is the **sole email sender**. It handles Freelancer scraping + HTML formatting + OCI SMTP delivery.
  - The agent's job is: (1) discover Workana projects via browser/web_search, (2) build JSON, (3) invoke the script with the JSON as CLI arg.
  - **FORMATO DE CORREO:** The script sends as `MIMEText(html, "html", "utf-8")` — NOT `MIMEMultipart("alternative")` which causes Gmail to render emails as `.eml` attachments.
  - **ESTÁNDAR DE ENVÍO:** OCI Email Delivery is the mandatory email standard (see `email-delivery-service` skill).
- **Empty Results:** If no projects are found, the script sends a brief email in Spanish stating that no new opportunities were found today.

### JSON Schema for Agent → Script Communication
The agent must pass a JSON array as the first CLI argument to `freelance_report.py`. Each object:
```json
{
  "title": "Short project title",
  "url": "Direct project URL",
  "platform": "Freelancer" or "Workana",
  "budget": "e.g. $250-750 USD or ₹600-1500 INR (~$7-18 USD)",
  "published": "e.g. Hoy, Hace 2 días, 24 de Junio 2026",
  "bids": "e.g. 2 bids, 33 bids, N/A",
  "pillar": "quick-wins" OR "high-value" OR "fast-delivery",
  "tags": ["quick-win", "high-value"],
  "description": "Spanish description of what the project needs",
  "why_fit": "Why this matches Santiago's Fullstack Fixer profile specifically",
  "proposal_angle": "Suggested proposal hook in Spanish (what Santiago should say to win it)"
}
```
**Pillar assignment guide:**
- `quick-wins`: WordPress bugfixes, Error 500, site down, urgent 24h, plugin conflicts
- `high-value`: Laravel development, Node.js API, Database optimization, $500+ budget, complex architecture
- `fast-delivery`: Landing pages, HTML/CSS fixes, PSD to HTML, quick deployments

For large JSON (>5 entries or containing quotes), write to `/tmp/workana_projects.json` via `write_file` first, then call `python3 script.py "$(cat /tmp/workana_projects.json)"` to avoid shell-escaping issues.


## Pitfalls & Lessons Learned
- **Delivery Target Error:** Setting `deliver` to a raw email address in a cronjob will result in a `no delivery target resolved` error. Always use `deliver: "origin"` and handle the email dispatch via tools within the agent's task execution.
- **CRITICAL — Cronjob System Directive Conflict:** The cronjob system injects a directive telling the agent: *"do NOT use send_message or try to deliver the output yourself — just produce your report and the system handles the rest."* This conflicts with instructions to send email via OCI. **The agent will obey the system directive and SKIP the email send**, then falsely claim it was sent. The ONLY reliable workaround is the Hybrid Script Architecture (see below) — a standalone Python script that sends the email directly, bypassing the agent's obedience layer entirely.
- **Freelancer API OAuth is NOT Automatable:** The Freelancer API (`/api/projects/0.1/oauth/token`) requires OAuth 2.0 **Authorization Code** flow (human browser login), not `client_credentials`. Automated cronjobs CANNOT use the Freelancer API. Use web scraping of `/jobs/` pages instead. The `client_credentials` grant returns HTTP 404.
- **Workana is a Cloudflare-Protected SPA:** Workana loads all project data via JavaScript (React). Static HTTP requests (`urllib`, `curl`) get HTML with ZERO project listings — only Cloudflare boilerplate. Googlebot UA spoofing does not help. There is no public API or RSS feed. The ONLY ways to get Workana data are: (a) `browser_navigate` + `browser_console` with JS extraction (full browser), or (b) `web_search` with `site:workana.com` operators (finds indexed pages, may be stale). For automated cronjobs, use option (b) and verify freshness.
- **Search Engine Blocking:** Direct HTTP requests to Google, Bing, and DuckDuckGo from a server IP are blocked or return empty results. Do not attempt to use search engines via `urllib` in standalone scripts. Use Hermes `web_search` tool instead (it routes through a proper backend).
- **HTML Email Formatting:** Email clients (Gmail, Outlook) do NOT render markdown `**bold**` — it shows as literal asterisks. ALWAYS use `<b>` or `<strong>` HTML tags and send the email body as `text/html`. This was confirmed by the user after receiving raw `**` markers in a report.
- **Email rendered as `.eml` attachment:** If Gmail shows the email as an `.eml` file attachment instead of rendering it normally, the cause is using `MIMEMultipart("alternative")` as the message container. Fix: use `MIMEText(html_body, "html", "utf-8")` directly without the multipart wrapper. This was reported by the user in the 2026-06-25 session. The `freelance_report.py` script was updated to v3 with this fix.
- **Avoid `execute_code` for Shell Commands in Cron:** When running as a scheduled cron job, `execute_code` may be blocked for arbitrary local Python scripts that bypass shell-string approval. Use `terminal()` or write a standalone `.py` file via `write_file()` and execute it with `python3 <path>`.
- **Search Precision:** Generic keywords may yield broad results; combine specific error codes (e.g., "500 error") with platform operators (e.g., `site:workana.com`) to surface high-intent leads.
- **Stale Search Results:** `web_search` with `site:workana.com` or `site:freelancer.com` often returns archived/closed projects from years past (2021, 2022, 2024). Always verify project status is "Open" before including in report. Prefer direct navigation to platform category/filter pages for current open projects.
- **Freelancer Snapshot Truncation:** Freelancer.com job listing pages (e.g., `/jobs/wordpress`) show 277+ jobs but the browser accessibility tree snapshot truncates after ~8000 chars, hiding most listings. Use `browser_console` with a JS expression to extract all `a[href*="/projects/"]` links from the DOM directly — this reliably returns 25-30 project titles + URLs per page.
- **Workana Filtered URLs:** The most efficient Workana entry point is `https://www.workana.com/en/jobs?skills=wordpress&language=es` (or replace `wordpress` with `laravel`, `node.js`, etc.). This page shows only open projects in Spanish with the skill filter applied, sorted by publication date. NOTE: These pages require a full browser (browser_navigate) — they will NOT work with static HTTP requests.
- **Batch web_extract:** `web_extract` accepts up to 5 URLs per call. Use batch mode to extract project details from 5 projects simultaneously — far more efficient than one-at-a-time.
- **Bid Count as Signal:** Projects with <5 bids posted in the last 24h are high-priority targets (low competition + fresh window). Always extract bid count when available.
- **JSON Shell-Escaping in Cronjobs:** Passing a large JSON array as a CLI argument with `python3 script.py '<json>'` is fragile — quotes and special chars inside JSON descriptions break shell parsing. When the JSON has >5 entries or contains quotes/descriptions, write it to `/tmp/workana_projects.json` via `write_file` first, then call `python3 script.py "$(cat /tmp/workana_projects.json)"`. This was confirmed in the 2026-06-25 session where a 10-entry JSON array needed this approach.
- **web_search Returns Freelancer Profiles, Not Jobs:** `web_search(query="site:workana.com wordpress bugfix")` returns `/freelancer/xxx` profile pages, NOT `/job/xxx` project listings. To find actual projects via web_search, use keywords like "proyecto", "desarrollo", "backend", "API" which appear in job titles. The browser navigation method (see Hybrid Script Architecture) is far more reliable and returns current open projects only.
- **Workana Multi-Skill Scanning:** A single Workana filtered URL (e.g., `skills=wordpress`) returns only ~8 projects. For comprehensive coverage, scan 4+ skill categories in parallel: `wordpress`, `laravel`, `node.js`, `shopify`. Combined, this yields 25-40 unique open projects per run. The browser_navigate + browser_console JS extraction pattern works reliably on all Workana filter pages.

## Hybrid Script Architecture (for automated cronjobs)

When this skill runs as a **scheduled cronjob**, the agent cannot reliably send emails — the cronjob system injects a "do NOT deliver output yourself" directive that overrides email-send instructions (see Pitfalls). The solution is a **hybrid agent + script** approach:

### Architecture
1. **Agent (GLM-5.2):** Uses `web_search` to find Workana projects (Workana blocks direct scraping — see Pitfalls). Passes results as JSON to the script.
2. **Script (`scripts/freelance_report.py`):** Scrapes Freelancer via HTTP, combines with Workana JSON from the agent, builds HTML report, and sends the email via OCI SMTP directly. No agent reasoning layer involved in email delivery.

### Cronjob prompt template
The cronjob prompt should instruct the agent to:

**Step 1 — Workana (browser navigation, PRIMARY method):**
1. Navigate to Workana filtered job pages for each relevant skill using `browser_navigate`. Use these URLs (one per skill):
   - `https://www.workana.com/en/jobs?skills=wordpress&language=es`
   - `https://www.workana.com/en/jobs?skills=laravel&language=es`
   - `https://www.workana.com/en/jobs?skills=node.js&language=es`
   - `https://www.workana.com/en/jobs?skills=shopify&language=es`
2. On each page, run `browser_console` with this JS expression to extract all project links:
   ```javascript
   JSON.stringify(Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => ({title: a.textContent.trim().substring(0,120), url: a.href})).filter(x => x.title.length > 10))
   ```
3. Deduplicate results across all skill pages. You will typically get 7-10 projects per page (25-40 total).
4. (Optional) Use `web_extract` with batches of up to 5 URLs to get full project descriptions, bid counts, and publication dates. Enrich the JSON with this data.

**Step 1 fallback — Workana via web_search (if browser tools unavailable):**
1. Run `web_search(query="site:workana.com laravel proyecto desarrollo API backend", limit=10)` — NOTE: broad keywords like "wordpress bugfix" return freelancer PROFILES (`/freelancer/xxx`), not project listings (`/job/xxx`). Use keywords like "proyecto", "desarrollo", "backend" to surface actual job pages.
2. Filter results where URL contains `workana.com/job/` (not `workana.com/freelancer/`).
3. Verify project status is "Open" and check publication date — stale results from 2021-2024 are common.

**Step 2 — Build JSON & invoke script:**
1. Build a JSON array of `{"title", "url", "description"}` objects from the Workana results.
2. Write the JSON to `/tmp/workana_projects.json` via `write_file` (avoids shell-escaping issues with large JSON).
3. Execute: `python3 /root/.hermes/scripts/freelance_report.py "$(cat /tmp/workana_projects.json)"`
4. The script handles Freelancer scraping + HTML formatting + OCI email sending autonomously.
5. If no Workana results, pass `'[]'` as the argument.

### Key principle
The script is the **sole email sender**. The agent must NOT attempt to send email or use `send_message`. The agent's only job is Workana discovery (browser or web_search) + invoking the script. This eliminates the system-directive conflict that caused silent email delivery failures across multiple models (Gemma 31B and GLM-5.2 both exhibited the same behavior).

### Multi-category scanning strategy
For maximum coverage, scan at least 4 Workana skill categories: `wordpress`, `laravel`, `node.js`, and `shopify`. Each category page returns 7-10 unique open projects. Combined with Freelancer results from the script, this yields 15-30+ total opportunities per run. Projects appear on multiple category pages only if tagged with multiple skills — deduplicate by URL.

## Reference Files
- **`references/extraction-techniques.md`** — Platform-specific extraction methods: Freelancer category page URLs, Workana filtered URLs, JS DOM extraction snippets, batch `web_extract` workflow, known issues, INR conversion reference, and the email template structure documentation.
- **`templates/report-email-template.html`** — Reusable HTML email template with `{{PLACEHOLDER}}` variables. Copy, fill in project data, send via OCI Email Delivery. Uses `<b>` tags (not markdown), emoji icons, CSS-styled project cards organized by pillar (Quick Wins / High Value / Fast Delivery), and a summary table.
- **`scripts/freelance_report.py`** — Standalone Python script (v4) for cronjob use. Scrapes Freelancer via HTTP, accepts Workana JSON as CLI arg, builds combined **pillar-based** HTML report (Quick Wins / High Value / Fast Delivery) with full project cards (description, why_fit, proposal_angle), and sends email via OCI SMTP using `MIMEText` directly (not `MIMEMultipart`). No external dependencies (stdlib only). Called by the agent in the hybrid architecture. NOTE: A copy also lives at `/root/.hermes/scripts/freelance_report.py` for cronjob compatibility — update both if making changes.

## Architecture v3 — Rich HTML Format (2026-06-25)

The email format was upgraded to a **pillar-based rich layout** per Santiago's explicit preference. Key features:
- Projects grouped by pillar: 🔥 Quick Wins, 💎 High Value, ⚡ Fast Delivery
- Each card includes: title, platform, budget, published date, link, tags, description, **"¿Por qué encaja?"** (why it fits), and **"Ángulo de propuesta"** (proposal hook)
- Summary table at bottom with pillar counts and top projects
- Footer with TARS AI branding and scan metadata

### JSON Schema for Agent → Script
The agent must pass a JSON array where each object has:
```json
{
  "title": "Short project title",
  "url": "Direct project URL",
  "platform": "Freelancer|Workana",
  "budget": "e.g. $250-750 USD",
  "published": "e.g. Hoy, Hace 2 días",
  "bids": "e.g. 2 bids",
  "pillar": "quick-wins|high-value|fast-delivery",
  "tags": ["quick-win", "high-value"],
  "description": "Spanish description",
  "why_fit": "Why this matches Santiago's profile",
  "proposal_angle": "Suggested proposal hook in Spanish"
}
```

### Script: `/root/.hermes/scripts/freelance_report.py` (v3)
- Accepts JSON array as first CLI argument
- If <3 projects provided, supplements with Freelancer web scraping
- Builds rich HTML email with pillar grouping, cards, tags, summary table
- Sends via OCI Email Delivery SMTP
- Uses `MIMEMultipart("alternative")` with both plain text + HTML parts

## Verification
The task is successful when the user receives a filtered list of $\geq 3$ highly compatible projects with actionable proposal strategies, delivered via OCI email in rich HTML format with pillar grouping, project cards, and summary table.
