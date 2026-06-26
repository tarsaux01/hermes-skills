---
name: whatsapp-automation
description: \"Unified guide for automating and managing WhatsApp communication via the wacli CLI.\"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [whatsapp, wacli, automation, messaging, search]
---

# WhatsApp Automation — Unified Orchestration Guide

This skill provides a class-level framework for using the `wacli` CLI to send messages, search conversations, and analyze chat history.

## 1. Tooling Architecture
The primary interface is the `wacli` binary.
- **Binary Path:** Commonly located at `/root/go/bin/wacli`.
- **Authentication:** Requires a paired session. If `not authenticated; run wacli auth` is encountered, the user must manually run `wacli auth` and scan the QR code.

## 2. Communication Workflows

### Sending Text Messages
Use the `send text` subcommand.
- **Command:** `wacli send text --to <phone_number> --message \"<text_content>\"`
- **Rules:**
  - **International Format:** Use the full phone number (e.g., `521...`) without the `+` sign.
  - **Required Flags:** Never use positional arguments; `--to` and `--message` are mandatory.
  - **Escaping:** Always wrap the message in double quotes to prevent shell errors with spaces or special characters.

### Sending Media Files
Use the `send file` subcommand.
- **Command:** `wacli send file --to <phone_number> --file <absolute_path>`
- **Requirement:** Ensure the path is absolute.

## 3. Discovery & Conversation Analysis

### Targeting Chats
To find the correct recipient or group:
1. **List Chats:** `wacli chats list --json` to obtain the `ChatJID` (useful for DMs).
2. **List Groups:** `wacli groups list` to obtain the specific JID for WhatsApp groups. **Crucial:** Use this specifically for groups, as `chats list` may be incomplete or omit group names.
3. **Confirm:** If using group names, verify the JID against the known group context.

### Extracting Context for Summaries
To reconstruct a conversation thread for analysis:
1. **Search:** Use `wacli messages search \"<keyword>\" --json` to isolate relevant messages.
2. **Filter:** Narrow the results by `Timestamp` to the desired window (e.g., the current day).
3. **Process:** Extract the `DisplayText` fields to build a chronological transcript.

## 5. Maintenance & Updates

### Updating the Client from Source
When updating the `wacli` binary from source, it is critical to enable CGO and the SQLite FTS5 module to avoid `no such module: fts5` errors in the database.

**Correct Build Command:**
```bash
cd /root/develop/wacli && \
CGO_ENABLED=1 CGO_CFLAGS="-Wno-error=missing-braces" \
go build -tags sqlite_fts5 -o /root/go/bin/wacli ./cmd/wacli
```
- `CGO_ENABLED=1`: Required for SQLite C bindings.
- `-tags sqlite_fts5`: Enables Full-Text Search support.
- `CGO_CFLAGS="-Wno-error=missing-braces"`: Prevents build failure on certain GCC versions.
