---
name: google-meet-bot
description: "Unified guide for deploying, managing, and post-processing Recall.ai meeting bots for Google Meet."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Recall-AI, Google-Meet, Meeting-Bots, n8n, Automation, Transcription]
---

# Google Meet Bot — Unified Orchestration Guide

This skill governs the deployment of Recall.ai bots and the event-driven pipelines used to process meeting transcripts from Google Meet.

## 1. Bot Dispatch Workflow
Recall.ai bots are triggered via API. Use the `dispatch_bot.py` script (located in the skill scripts directory) to handle authentication and payload construction.

- **Standard Command:** `python3 /root/.hermes/skills/productivity/google-meet-bot/scripts/dispatch_bot.py --url \"<MEETING_URL>\"`
- **Scheduled Joins:** Add `--time \"ISO_TIMESTAMP\"` to the command.
- **Default Config:** Video: False, Audio: True, Transcript: True (Batch/Async mode).

### ⚠️ Critical: Regional Endpoints & Cost Optimization
- **Region:** Default for TARS AI Assistant is `us-west-2`.
- **Cost Control:** To maintain the **Standard Bot rate ($0.10/hr)**, avoid `recallai_streaming` providers. Use the default `recallai` provider for asynchronous (batch) transcription to avoid GPU-tier billing ($1.00/hr).
- **Auth Format:** Always use `Authorization: Token <TOKEN>`. (Note: `Bearer` is not supported for the `/api/v1/bot` endpoint).

## 2. Post-Processing Pipeline (n8n)
For high-quality summaries, use a hub-and-spoke architecture in n8n to avoid webhook timeouts and ensure complete data retrieval.

### Workflow Architecture
1. **Ingress (Hub):** A single Webhook node receives all Recall events. Return `200 OK` immediately.
2. **Filtering:** Route only `transcript.done` (and optionally `recording.done`) events to the analysis spoke.
3. **Data Retrieval:** Use the `meeting_id` from the webhook to fetch the full transcript via `GET /api/v1/meetings/{meeting_id}/transcript/`.
4. **LLM Analysis:** Pass the full text to an LLM with a structured prompt (Executive Summary, Decisions, Action Items, Sentiment).

### Event Chain
- `recording.done` $\rightarrow$ Trigger transcription process via POST to `/transcripts/`.
- `transcript.done` $\rightarrow$ Fetch transcript $\rightarrow$ Analysis $\rightarrow$ Delivery.

## 3. Tooling & Verification
- **MCP Server:** Use the `recall-ai` MCP server for read-only access to bots, logs, and recordings for faster debugging.
- **Cleanup Script:** Use `~/.hermes/scripts/recall_cleanup.py` to delete bots and recordings older than 7 days to avoid storage costs. This is automated via a daily cronjob at 03:00 AM.
- **Validation:** Simulate the data flow (Webhook $\rightarrow$ API Fetch $\rightarrow$ LLM) using a local script before deploying to n8n to verify prompt effectiveness.
- **Scripts:**
    - `scripts/dispatch_bot.py`: Dispatches bots with cost-optimized settings.
    - `scripts/recall_cleanup.py`: Daily maintenance script to delete recordings older than 7 days.

## 4. Troubleshooting
- **401 Unauthorized:** Likely a region mismatch. Check the `BASE_URL` against the account's region.
- **Missing Transcripts:** Ensure both `recording.done` and `transcript.done` events are enabled in the Recall.ai dashboard.
- **Auth Format:** Always use `Authorization: Token <TOKEN>` (Note: `Bearer` is not supported for the `/api/v1/bot` endpoint).

## 5. Future Roadmap & Ideas
- **Auto-Deletion Policy:** Implement a cleanup routine to delete transcripts and audio files automatically after 5 days to reduce storage costs and improve privacy.
- **Auto-Expiration Check:** Investigate if Recall.ai supports native TTL (Time-To-Live) or expiration dates for recordings via API, or if a custom cronjob is required to handle the deletion based on the `created_at` date.
- **Cost Optimization (Real-time vs. Batch):** Investigate and disable \"Real-time Transcription\" if it's triggering the GPU/High-tier rate ($1.00/hr). Ensure the bot is configured for \"Post-meeting\" or \"Batch\" transcription to maintain the $0.10/hr standard rate.
