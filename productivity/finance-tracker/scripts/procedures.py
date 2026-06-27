#!/usr/bin/env python3
"""
Toshl Procedures — High-level operations built on top of toshl_client.py.
Each function here is a reusable procedure that can be called from the agent
or from cron jobs.
"""

import sys
import os
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from toshl_client import ToshlClient


def clean_duplicate_categories():
    """
    Clean up duplicate/erroneous categories:
    1. Delete 'banca' (empty, created by error)
    2. Move 1 entry from 'Emergente/NoPlaneadoe' → 'Emergente/NoPlaneado', then delete the typo category
    3. Rename tag 'Lub' → 'Lubricante Íntimo'
    """
    client = ToshlClient()
    
    # ─── 1. Delete 'banca' (73623144) ───
    print("=== 1. Deleting 'banca' (73623144) ===")
    resp = client.delete_category("73623144")
    print(f"  Deleted: {resp}")
    
    # ─── 2. Move entry from 'Emergente/NoPlaneadoe' → 'Emergente/NoPlaneado' ───
    print("\n=== 2. Fixing 'Emergente/NoPlaneadoe' (73711170) ===")
    entries = client.list_entries(category="73711170", from_date="2020-01-01", to_date="2026-12-31")
    print(f"  Found {len(entries)} entries in typo category")
    
    correct_cat = "63328377"  # Emergente/NoPlaneado
    
    for entry in entries:
        print(f"  Moving entry {entry['id']}: {entry.get('date','')} | {entry.get('amount',0)} | {entry.get('desc','')}")
        client.update_entry(entry["id"], category=correct_cat)
        print(f"    → Moved to category {correct_cat}")
    
    # Now delete the typo category
    resp = client.delete_category("73711170")
    print(f"  Deleted typo category: {resp}")
    
    # ─── 3. Rename tag 'Lub' → 'Lubricante Íntimo' ───
    print("\n=== 3. Renaming tag 'Lub' (52684867) ===")
    client.update_tag("52684867", name="Lubricante Íntimo")
    print("  Renamed: Lub → Lubricante Íntimo")
    
    # ─── Refresh local map ───
    print("\n=== Refreshing local map ===")
    client.refresh_local_map()
    print("\n✅ Cleanup complete!")


def register_expense(amount: float, category_name: str, account_name: str = "Efectivo",
                     desc: str = "", tags: Optional[list] = None, date: Optional[str] = None):
    """
    Quick-register an expense using natural language names.
    Resolves names to IDs using the local map.
    """
    from datetime import datetime
    
    client = ToshlClient()
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Resolve category
    cat = client.resolve_category(category_name)
    if not cat:
        print(f"❌ Category '{category_name}' not found in map. Run refresh-map first.")
        return None
    
    # Resolve account
    acc = client.resolve_account(account_name)
    if not acc:
        print(f"❌ Account '{account_name}' not found in map. Run refresh-map first.")
        return None
    
    # Resolve tags
    tag_ids = []
    if tags:
        for tag_name in tags:
            tag_id = client.resolve_tag(tag_name)
            if tag_id:
                tag_ids.append(tag_id)
            else:
                print(f"⚠️ Tag '{tag_name}' not found, skipping.")
    
    # Create entry (negative for expense)
    entry = client.create_entry(
        amount=-abs(amount),
        date=date,
        account=acc["id"],
        category=cat["id"],
        desc=desc,
        tags=tag_ids if tag_ids else None,
    )
    
    print(f"✅ Registered: ${amount:.2f} {acc.get('currency','MXN')} in '{category_name}' ({account_name})")
    if desc:
        print(f"   Description: {desc}")
    if tag_ids:
        print(f"   Tags: {', '.join(tags)}")
    return entry


def register_income(amount: float, category_name: str, account_name: str = "Efectivo",
                    desc: str = "", tags: Optional[list] = None, date: Optional[str] = None):
    """
    Quick-register an income using natural language names.
    """
    from datetime import datetime
    
    client = ToshlClient()
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    cat = client.resolve_category(category_name)
    if not cat:
        print(f"❌ Category '{category_name}' not found.")
        return None
    
    acc = client.resolve_account(account_name)
    if not acc:
        print(f"❌ Account '{account_name}' not found.")
        return None
    
    tag_ids = []
    if tags:
        for tag_name in tags:
            tag_id = client.resolve_tag(tag_name)
            if tag_id:
                tag_ids.append(tag_id)
    
    entry = client.create_entry(
        amount=abs(amount),
        date=date,
        account=acc["id"],
        category=cat["id"],
        desc=desc,
        tags=tag_ids if tag_ids else None,
    )
    
    print(f"✅ Registered income: +${amount:.2f} {acc.get('currency','MXN')} in '{category_name}' ({account_name})")
    return entry


def monthly_report(month: int = None, year: int = None):
    """
    Generate a formatted monthly report with totals by category.
    """
    from datetime import datetime
    import calendar
    
    client = ToshlClient()
    
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    # Calculate date range
    last_day = calendar.monthrange(year, month)[1]
    from_date = f"{year}-{month:02d}-01"
    to_date = f"{year}-{month:02d}-{last_day:02d}"
    
    entries = client.list_entries(from_date=from_date, to_date=to_date)
    
    if not entries:
        print(f"No entries found for {year}-{month:02d}")
        return
    
    # Load map for category names
    m = client.load_local_map()
    cat_names = {v["id"]: k for k, v in m["categories"].items()}
    
    # Aggregate
    expenses = {}
    incomes = {}
    total_expense = 0
    total_income = 0
    
    for e in entries:
        amount = e.get("amount", 0)
        cat_id = e.get("category", "unknown")
        cat_name = cat_names.get(cat_id, f"Unknown ({cat_id})")
        
        if amount < 0:
            expenses[cat_name] = expenses.get(cat_name, 0) + abs(amount)
            total_expense += abs(amount)
        else:
            incomes[cat_name] = incomes.get(cat_name, 0) + amount
            total_income += amount
    
    # Print report
    month_name = calendar.month_name[month]
    print(f"\n📊 Reporte: {month_name} {year}")
    print(f"   Total entradas: {len(entries)}")
    print(f"\n💰 INGRESOS: ${total_income:,.2f} MXN")
    for cat, amt in sorted(incomes.items(), key=lambda x: -x[1]):
        print(f"   {cat}: ${amt:,.2f}")
    
    print(f"\n💸 GASTOS: ${total_expense:,.2f} MXN")
    for cat, amt in sorted(expenses.items(), key=lambda x: -x[1]):
        print(f"   {cat}: ${amt:,.2f}")
    
    balance = total_income - total_expense
    emoji = "📈" if balance >= 0 else "📉"
    print(f"\n{emoji} BALANCE: ${balance:,.2f} MXN")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Toshl Procedures")
    sub = parser.add_subparsers(dest="command")
    
    sub.add_parser("clean", help="Run cleanup procedures")
    
    rep = sub.add_parser("report", help="Generate monthly report")
    rep.add_argument("--month", type=int, help="Month (1-12)")
    rep.add_argument("--year", type=int, help="Year (e.g. 2026)")
    
    exp = sub.add_parser("expense", help="Register an expense")
    exp.add_argument("amount", type=float, help="Amount")
    exp.add_argument("category", help="Category name")
    exp.add_argument("--account", default="Efectivo", help="Account name")
    exp.add_argument("--desc", default="", help="Description")
    exp.add_argument("--tags", nargs="*", help="Tag names")
    
    inc = sub.add_parser("income", help="Register an income")
    inc.add_argument("amount", type=float, help="Amount")
    inc.add_argument("category", help="Category name")
    inc.add_argument("--account", default="Efectivo", help="Account name")
    inc.add_argument("--desc", default="", help="Description")
    
    args = parser.parse_args()
    
    if args.command == "clean":
        clean_duplicate_categories()
    elif args.command == "report":
        monthly_report(args.month, args.year)
    elif args.command == "expense":
        register_expense(args.amount, args.category, args.account, args.desc, args.tags)
    elif args.command == "income":
        register_income(args.amount, args.category, args.account, args.desc)
    else:
        parser.print_help()