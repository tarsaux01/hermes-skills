import requests
import argparse
import sys
import os
from datetime import datetime

# Configuration
# It is recommended to set RECALL_AI_TOKEN as an environment variable
DEFAULT_TOKEN=os.getenv("RECALL_AI_TOKEN", "c8e8481c0ca7e6ec587918ad9dca5ff83691a554")
DEFAULT_REGION = "us-west-2"
DEFAULT_BOT_NAME = "TARS AI Assistant"
BASE_URL = f"https://{DEFAULT_REGION}.recall.ai"

def dispatch_bot(meeting_url, scheduled_time=None):
    endpoint = f"{BASE_URL}/api/v1/bot"
    
    payload = {
        "meeting_url": meeting_url,
        "bot_name": DEFAULT_BOT_NAME,
        "recording_config": {}
    }
    
    if scheduled_time:
        payload["scheduled_start_time"] = scheduled_time

    headers = {
        "Authorization": f"Token {DEFAULT_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"🚀 Dispatching bot '{DEFAULT_BOT_NAME}' to: {meeting_url}...")
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Success! Bot ID: {data.get('id')}")
        print(f"Meeting ID: {data.get('meeting_id')}")
        return data
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if response.status_code == 401:
            print("⚠️ Possible Region Mismatch or Invalid Token (401 Unauthorized).")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recall.ai Bot Dispatcher")
    parser.add_argument("--url", required=True, help="The Google Meet/Zoom URL")
    parser.add_argument("--time", help="ISO timestamp for scheduled join (e.g. 2026-06-25T10:00:00Z)")
    
    args = parser.parse_args()
    dispatch_bot(args.url, args.time)
