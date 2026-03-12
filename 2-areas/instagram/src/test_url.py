#!/usr/bin/env python3
import os
import json
import time
import requests
from dotenv import load_dotenv

creds_path = os.path.expanduser("~/.openclaw/workspace/credentials/apify-creds.env")
load_dotenv(creds_path)
api_token = os.getenv("APIFY_TOKEN")

actor_id = "apify~instagram-scraper"
base_url = "https://api.apify.com/v2"

# Try with direct URL approach
run_input = {
    "directUrls": ["https://www.instagram.com/instagram/"],
    "resultsLimit": 20,
    "resultsType": "posts"
}

print("Testing with direct URL...")
print(json.dumps(run_input, indent=2))

run_url = f"{base_url}/acts/{actor_id}/runs"
headers = {"Content-Type": "application/json"}
params = {"token": api_token}

response = requests.post(run_url, json=run_input, headers=headers, params=params, timeout=30)
response.raise_for_status()

run_id = response.json()["data"]["id"]
print(f"\nRun ID: {run_id}")

# Wait
run_url = f"{base_url}/actor-runs/{run_id}"
for i in range(60):
    time.sleep(3)
    response = requests.get(run_url, params=params, timeout=30)
    run_data = response.json()["data"]
    status = run_data["status"]
    
    if status == "SUCCEEDED":
        print("✅ Completed")
        break
    elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
        print(f"❌ {status}")
        exit(1)
    
    print(f"⏳ {status}...")

# Get results
dataset_id = run_data["defaultDatasetId"]
dataset_url = f"{base_url}/datasets/{dataset_id}/items"
params["format"] = "json"

response = requests.get(dataset_url, params=params, timeout=60)
data = response.json()

print(f"\n✅ Got {len(data)} items")

if data and "error" not in data[0]:
    print(f"\nSuccess! First post keys: {list(data[0].keys())[:10]}")
    
    os.makedirs("../output", exist_ok=True)
    with open("../output/test-url-method.json", "w") as f:
        json.dump(data[:2], f, indent=2)
    print("💾 Saved to output/test-url-method.json")
else:
    print("\n❌ Error:")
    print(json.dumps(data[:1], indent=2))
