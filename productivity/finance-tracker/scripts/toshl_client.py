#!/usr/bin/env python3
"""
Toshl API Client — Base client for all Toshl operations.
Handles auth, pagination, rate limiting, and CRUD operations.
"""

import os
import json
import time
import requests
from typing import Optional, List, Dict, Any


class ToshlClient:
    """Thin wrapper around the Toshl REST API."""
    
    BASE_URL = "https://api.toshl.com"
    
    def __init__(self, token: Optional[str] = None):
        """Initialize client. Reads token from .env if not provided."""
        if token is None:
            token = self._read_token_from_env()
        if not token:
            raise ValueError("No Toshl API token found. Set TOSHL_API_TOKEN in .env")
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
    
    @staticmethod
    def _read_token_from_env() -> Optional[str]:
        """Read TOSHL_API_TOKEN from Hermes .env file."""
        env_path = os.path.expanduser("~/.hermes/.env")
        if not os.path.exists(env_path):
            return None
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("TOSHL_API_TOKEN="):
                    return line.split("=", 1)[1].strip()
        return None
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                 data: Optional[Dict] = None, retries: int = 3) -> requests.Response:
        """Make an authenticated request with retry logic."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        for attempt in range(retries):
            resp = requests.request(method, url, headers=self.headers,
                                    params=params, json=data)
            # Rate limit handling
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 60))
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            # Retry on 5xx
            if resp.status_code >= 500 and attempt < retries - 1:
                print(f"Server error {resp.status_code}, retrying ({attempt+1}/{retries})...")
                time.sleep(2 ** attempt)
                continue
            return resp
        return resp
    
    # ─── CATEGORIES ───
    
    def list_categories(self, category_type: Optional[str] = None) -> List[Dict]:
        """List all categories. Filter by 'expense', 'income', or 'system'."""
        params = {}
        if category_type:
            params["type"] = category_type
        resp = self._request("GET", "/categories", params=params)
        resp.raise_for_status()
        return resp.json()
    
    def get_category(self, cat_id: str) -> Dict:
        """Get a single category by ID."""
        resp = self._request("GET", f"/categories/{cat_id}")
        resp.raise_for_status()
        return resp.json()
    
    def update_category(self, cat_id: str, **fields) -> Dict:
        """Update a category. Pass fields like name='New Name'."""
        resp = self._request("PUT", f"/categories/{cat_id}", data=fields)
        resp.raise_for_status()
        return resp.json()
    
    def delete_category(self, cat_id: str) -> bool:
        """Delete a category. Returns True on success."""
        resp = self._request("DELETE", f"/categories/{cat_id}")
        return resp.status_code in (200, 204)
    
    # ─── ACCOUNTS ───
    
    def list_accounts(self) -> List[Dict]:
        """List all accounts."""
        resp = self._request("GET", "/accounts")
        resp.raise_for_status()
        return resp.json()
    
    def get_account(self, acc_id: str) -> Dict:
        """Get a single account by ID."""
        resp = self._request("GET", f"/accounts/{acc_id}")
        resp.raise_for_status()
        return resp.json()
    
    # ─── ENTRIES ───
    
    def list_entries(self, from_date: Optional[str] = None, to_date: Optional[str] = None,
                     category: Optional[str] = None, account: Optional[str] = None,
                     tags: Optional[str] = None, per_page: int = 200) -> List[Dict]:
        """
        List entries with optional filters.
        Dates must be YYYY-MM-DD format.
        category/account/tags accept IDs.
        Handles pagination automatically.
        """
        params = {"per_page": per_page}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if category:
            params["category"] = category
        if account:
            params["account"] = account
        if tags:
            params["tags"] = tags
        
        all_entries = []
        page = 0
        while True:
            params["page"] = page
            resp = self._request("GET", "/entries", params=params)
            resp.raise_for_status()
            entries = resp.json()
            all_entries.extend(entries)
            if len(entries) < per_page:
                break
            page += 1
        return all_entries
    
    def create_entry(self, amount: float, date: str, account: str, category: str,
                     desc: str = "", currency: Optional[Dict] = None,
                     tags: Optional[List[str]] = None, completed: bool = True) -> Dict:
        """
        Create a new entry.
        - amount: Negative for expense, positive for income.
        - date: YYYY-MM-DD
        - account: Account ID
        - category: Category ID
        - tags: List of tag IDs
        """
        data = {
            "amount": amount,
            "date": date,
            "account": account,
            "category": category,
            "desc": desc,
            "completed": completed,
        }
        if currency:
            data["currency"] = currency
        if tags:
            data["tags"] = tags
        resp = self._request("POST", "/entries", data=data)
        resp.raise_for_status()
        return resp.json()
    
    def update_entry(self, entry_id: str, **fields) -> Dict:
        """Update an entry. Pass fields like amount=-50, category='123', etc."""
        resp = self._request("PUT", f"/entries/{entry_id}", data=fields)
        resp.raise_for_status()
        return resp.json()
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry. Returns True on success."""
        resp = self._request("DELETE", f"/entries/{entry_id}")
        return resp.status_code in (200, 204)
    
    # ─── TAGS ───
    
    def list_tags(self) -> List[Dict]:
        """List all tags."""
        resp = self._request("GET", "/tags")
        resp.raise_for_status()
        return resp.json()
    
    def get_tag(self, tag_id: str) -> Dict:
        """Get a single tag by ID."""
        resp = self._request("GET", f"/tags/{tag_id}")
        resp.raise_for_status()
        return resp.json()
    
    def update_tag(self, tag_id: str, **fields) -> Dict:
        """Update a tag. Pass fields like name='New Name'."""
        resp = self._request("PUT", f"/tags/{tag_id}", data=fields)
        resp.raise_for_status()
        return resp.json()
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag. Returns True on success."""
        resp = self._request("DELETE", f"/tags/{tag_id}")
        return resp.status_code in (200, 204)
    
    # ─── USER / MISC ───
    
    def get_me(self) -> Dict:
        """Get current user info."""
        resp = self._request("GET", "/me")
        resp.raise_for_status()
        return resp.json()
    
    def get_rate_limit(self) -> Dict:
        """Check current rate limit status."""
        resp = self._request("GET", "/rate-limit")
        if resp.status_code == 404:
            return {"limit": "N/A", "remaining": "N/A"}
        resp.raise_for_status()
        return resp.json()
    
    # ─── LOCAL MAP HELPERS ───
    
    def load_local_map(self) -> Dict:
        """Load the cached category/account/tag map from references/toshl_map.json."""
        map_path = os.path.join(os.path.dirname(__file__), "..", "references", "toshl_map.json")
        with open(map_path, "r") as f:
            return json.load(f)
    
    def resolve_category(self, name: str) -> Optional[Dict]:
        """Resolve a category name to its ID using the local map."""
        m = self.load_local_map()
        return m.get("categories", {}).get(name)
    
    def resolve_account(self, name: str) -> Optional[Dict]:
        """Resolve an account name to its ID using the local map."""
        m = self.load_local_map()
        return m.get("accounts", {}).get(name)
    
    def resolve_tag(self, name: str) -> Optional[str]:
        """Resolve a tag name to its ID using the local map."""
        m = self.load_local_map()
        return m.get("tags", {}).get(name)
    
    def refresh_local_map(self) -> Dict:
        """Re-download all categories/accounts/tags and update the local map file."""
        cats = self.list_categories()
        accs = self.list_accounts()
        tags = self.list_tags()
        
        cat_map = {c["name"]: {"id": c["id"], "type": c.get("type", "")} for c in cats}
        acc_map = {a["name"]: {"id": a["id"], "currency": a.get("currency", {}).get("code", "MXN")} for a in accs}
        tag_map = {t["name"]: t["id"] for t in tags}
        
        output = {
            "categories": cat_map,
            "accounts": acc_map,
            "tags": tag_map,
            "currency_main": "MXN",
        }
        
        map_path = os.path.join(os.path.dirname(__file__), "..", "references", "toshl_map.json")
        os.makedirs(os.path.dirname(map_path), exist_ok=True)
        with open(map_path, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Map refreshed: {len(cat_map)} categories, {len(acc_map)} accounts, {len(tag_map)} tags")
        return output


# ─── CLI ENTRY POINT ───

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Toshl API Client")
    sub = parser.add_subparsers(dest="command")
    
    # info
    sub.add_parser("info", help="Show user info and rate limit")
    
    # list
    list_p = sub.add_parser("list", help="List resources")
    list_p.add_argument("resource", choices=["categories", "accounts", "tags", "entries"])
    list_p.add_argument("--from", dest="from_date", help="Start date YYYY-MM-DD")
    list_p.add_argument("--to", dest="to_date", help="End date YYYY-MM-DD")
    list_p.add_argument("--category", help="Filter by category ID")
    
    # refresh
    sub.add_parser("refresh-map", help="Re-download and save local map")
    
    # clean (placeholder)
    sub.add_parser("clean", help="Run cleanup procedures")
    
    args = parser.parse_args()
    client = ToshlClient()
    
    if args.command == "info":
        me = client.get_me()
        rl = client.get_rate_limit()
        print(f"User: {me.get('name', 'N/A')}")
        print(f"Email: {me.get('email', 'N/A')}")
        print(f"Rate limit: {rl.get('remaining', 'N/A')}/{rl.get('limit', 'N/A')}")
    
    elif args.command == "list":
        if args.resource == "categories":
            for c in client.list_categories():
                print(f"  [{c['id']}] {c['name']} ({c.get('type','')}) — {c.get('counts',{}).get('entries',0)} entries")
        elif args.resource == "accounts":
            for a in client.list_accounts():
                print(f"  [{a['id']}] {a['name']} — {a.get('balance',0)} {a.get('currency',{}).get('code','')}")
        elif args.resource == "tags":
            for t in client.list_tags():
                print(f"  [{t['id']}] {t['name']}")
        elif args.resource == "entries":
            entries = client.list_entries(from_date=args.from_date, to_date=args.to_date,
                                         category=args.category)
            print(f"Total: {len(entries)} entries")
            for e in entries[:20]:
                print(f"  {e.get('date','')} | {e.get('amount',0):>10.2f} | {e.get('desc','')}")
    
    elif args.command == "refresh-map":
        client.refresh_local_map()
    
    elif args.command == "clean":
        print("Run: python3 procedures.py clean")
    
    else:
        parser.print_help()