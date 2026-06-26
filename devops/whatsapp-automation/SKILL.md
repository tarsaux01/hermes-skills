---
name: whatsapp-automation
description: "Unified guide for automating and managing WhatsApp communication via the wacli CLI, including natural language intent mapping and voice synthesis."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [whatsapp, wacli, automation, messaging, search, voice, elevenlabs]
---

# WhatsApp Automation — Unified Orchestration Guide

This skill provides a framework for using the `wacli` CLI to manage communications, with an emphasis on natural language execution and voice synthesis via ElevenLabs.

## 1. Intent Mapping (Conceptual Execution)
When the user provides a natural language request (e.g., "Send a message to Paul", "Manda un audio a mi papá"), follow this internal logic:

### Step A: Contact Resolution
**Never assume a phone number.** Always resolve the contact first:
1. Search for the name in the **Silo de Contactos** (using `skill-silo-contacts`).
2. Extract the phone number in international format (e.g., `521...`).
3. If the contact is ambiguous or not found, use `clarify` to ask the user.

### Step B: Modality Selection
- **Text:** If the request is "send a message", "write to", or "tell X", use the **Text Workflow**.
- **Voice/Audio:** If the request is "send an audio", "voice note", or "record a message", use the **Voice Workflow**.

## 2. Communication Workflows

### 💬 Text Workflow
- **Command:** `wacli send text --to <phone_number> --message \"<text_content>\"`
- **Rule:** Always wrap the message in double quotes. Use the resolved number from the Contact Silo.

### 🎙️ Voice Workflow (ElevenLabs Integration)
To send a voice note, chain the TTS tool with the file sender:
1. **Synthesis:** Call `text_to_speech(text="<content>")`. 
   - *Note:* This uses the configured **ElevenLabs** provider to generate a high-quality voice file.
2. **Capture Path:** Get the absolute path to the generated `.mp3` file from the tool output.
3. **Dispatch:** Use the `send file` subcommand.
   - **Command:** `wacli send file --to <phone_number> --file <absolute_path_to_mp3>`

## 3. Tooling Architecture
- **Binary Path:** `/root/go/bin/wacli`.
- **Authentication:** If `not authenticated` is encountered, prompt the user to run `wacli auth` manually.

## 4. Discovery & Conversation Analysis

### Targeting Chats & Groups
1. **DMs:** `wacli chats list --json` to obtain the `ChatJID`.
2. **Groups:** `wacli groups list` to obtain the specific JID for groups. **Crucial:** Always use this for group targets.

### Context Extraction
To summarize or analyze a thread:
1. **Search:** `wacli messages search \"<keyword>\" --json`.
2. **Filter:** Narrow by `Timestamp` to the relevant window.
3. **Process:** Extract `DisplayText` to build the transcript.

## 5. Maintenance & Updates
**Correct Build Command (with FTS5 for search):**
```bash
cd /root/develop/wacli && \
CGO_ENABLED=1 CGO_CFLAGS="-Wno-error=missing-braces" \
go build -tags sqlite_fts5 -o /root/go/bin/wacli ./cmd/wacli
```
