---
name: whatsapp-automation
description: "Unified guide for automating and managing WhatsApp communication via the wacli CLI, including natural language intent mapping, voice synthesis, and automated contact synchronization."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [whatsapp, wacli, automation, messaging, search, voice, elevenlabs, contacts-sync]
---

# WhatsApp Automation — Unified Orchestration Guide

This skill provides a framework for using the `wacli` CLI to manage communications, with an emphasis on natural language execution, voice synthesis via ElevenLabs, and automated contact management.

## 1. Intent Mapping & Contact Resolution
When the user provides a request (e.g., "Send a message to Paul", "Manda un audio al grupo de la familia"), follow this resolution hierarchy:

### Step A: Resolution Hierarchy
1.  **Silo Check:** Search for the name in the **Silo de Contactos** (using `skill-silo-contacts`). If found, use the associated phone number.
2.  **WACLI Discovery:** If not in the silo, search using `wacli`:
    - **For Individuals:** Use `wacli chats list --json` and search for the name in the output to find the matching `ChatJID`/number.
    - **For Groups:** Use `wacli groups list` to find the specific group name and its JID.
3.  **Ambiguity Handling:** If multiple matches are found or no match exists, use `clarify` to ask the user.

### Step B: Automated Silo Synchronization (The "Learning" Loop)
If a contact/group was discovered via `wacli` but was missing from the Silo:
- **High Confidence:** If there is a unique, clear match, automatically save the contact/group details (Name, Phone/JID) into the **Silo de Contactos** to avoid searching `wacli` next time.
- **Low Confidence:** If there is any doubt or multiple similar names, ask the user for confirmation: *"Encontré a 'Paul' en WhatsApp pero no en tus contactos, ¿quieres que lo guarde en tu Silo de Contactos?"*

## 2. Communication Workflows

### 💬 Text Workflow
- **Command:** `wacli send text --to <phone_number> --message \"<text_content>\"`
- **Rule:** Always wrap the message in double quotes.

### 🎙️ Voice Workflow (ElevenLabs Integration)
To send a voice note, chain the TTS tool with the file sender:
1. **Synthesis:** Call `text_to_speech(text="<content>")`. 
   - *Note:* This uses the configured **ElevenLabs** provider to generate a high-quality voice file.
2. **Capture Path:** Get the absolute path to the generated `.mp3` file.
3. **Dispatch:** Use the `send file` subcommand.
   - **Command:** `wacli send file --to <phone_number> --file <absolute_path_to_mp3>`

## 3. Tooling Architecture
- **Binary Path:** `/root/go/bin/wacli`.
- **Authentication:** If `not authenticated` is encountered, prompt the user to run `wacli auth` manually.

## 4. Discovery & Conversation Analysis

### Targeting Chats & Groups
- **DMs:** `wacli chats list --json` to obtain the `ChatJID`.
- **Groups:** `wacli groups list` to obtain the specific JID for groups.

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
