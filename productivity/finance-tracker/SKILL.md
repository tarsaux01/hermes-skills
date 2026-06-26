---
name: finance-tracker
description: "Unified orchestration for personal finance management via Toshl API. Handles expense/income tracking, ticket auto-classification via vision, and financial reporting."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [toshl, finance, expense-tracking, vision, automation]
---

# Finance Tracker — Toshl Integration Guide

This skill transforms the agent into a financial assistant capable of managing the user's Toshl account. It focuses on low-friction entry (voice/text/images) and high-precision reporting.

## 1. Intent Mapping (Conceptual Execution)
The agent should trigger this skill when the user mentions money, expenses, budgets, or specifically "Toshl".

### Trigger Patterns:
- **Registration:** "Anota que gasté X en Y", "Suma X a la categoría Z", "Registra un ingreso de X".
- **Inquiry:** "¿Cuánto he gastado en [Categoría]?", "¿Cuál es mi balance?", "Dame un reporte de este mes".
- **Visual Entry:** Sending an image of a receipt/ticket $\rightarrow$ Trigger "Ticket Auto-Classification" flow.

## 2. Operational Workflows

### 💬 Entry Workflow (Manual)
1. **Parse:** Extract Amount, Currency, Category, and Date from the user's request.
2. **Category Match:** Check if the category exists in Toshl. If ambiguous, use `clarify`.
3. **Execution:** Call the Toshl API via `POST /v1/entries`.
   - **Auth:** Use `Authorization: Bearer <TOKEN>`.

### 📸 Ticket Auto-Classification (Vision)
When an image of a receipt is received:
1. **Analysis:** Use `vision_analyze` to extract:
   - Merchant/Store name.
   - Total amount and currency.
   - Date of transaction.
   - Items purchased (for detailed categorization).
2. **Classification:** Map the merchant/items to the most likely Toshl category (e.g., "Starbucks" $\rightarrow$ "Coffee/Dining").
3. **Confirmation:** Present the extracted data to the user: *"He detectado un gasto de $X en [Comercio]. ¿Lo registro en la categoría [Categoría]?"*
4. **Dispatch:** Upon approval, send to Toshl API.

### 📊 Reporting Workflow
1. **Data Fetch:** Use `GET /v1/entries` with date filters.
2. **Processing:** Use Python to aggregate totals by category or date.
3. **Delivery:** Present a clean, formatted summary (bullet lists, bold totals) directly in the chat.

## 3. Technical Specification (Toshl API)
- **Base URL:** `https://api.toshl.com/v1`
- **Auth Method:** Bearer Token (`Authorization: Bearer {token}`).
- **Key Endpoints:**
  - `GET /accounts`: List available accounts.
  - `GET /categories`: List categories for mapping.
  - `POST /entries`: Create a new financial entry.
  - `GET /entries`: Retrieve history for reports.

## 4. Maintenance
- **Token Rotation:** If a `401 Unauthorized` is returned, prompt the user for a new OAuth token.
- **Category Sync:** Periodically refresh the local category map to match Toshl's current setup.
