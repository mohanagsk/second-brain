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

# Test with Instagram's official account (definitely public)
run_input = {
    "username": ["instagram"],
    "resultsLimit": 20,
    "resultsType": "posts",
    "searchType": "user",
    "searchLimit": 1,
    "addParentData": False
}

print("Testing with @instagram (official account)...")
print(json.dumps(run_input, indent=2))

run_url = f"{base_url}/acts/{actor_id}/runs"
headers = {"Content-Type": "application/json"}
params = {"token": api_token}

response = requests.post(run_url, json=run_input, headers=headers, params=params, timeout=30)
response.raise_for_status()

run_id = response.json()["data"]["id"]
print(f"\nRun ID: {run_id}")

# Wait for completion
run_url = f"{base_url}/actor-runs/{run_id}"
while True:
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
    time.sleep(3)

# Get results
dataset_id = run_data["defaultDatasetId"]
dataset_url = f"{base_url}/datasets/{dataset_id}/items"
params["format"] = "json"

response = requests.get(dataset_url, params=params, timeout=60)
data = response.json()

print(f"\n✅ Got {len(data)} posts from @instagram")

if data and "error" not in data[0]:
    print(f"\nFirst post keys: {list(data[0].keys())}")
    print(f"Sample post ID: {data[0].get('id') or data[0].get('pk')}")
    print(f"Likes: {data[0].get('like_count') or data[0].get('likeCount')}")
    
    # Save sample
    os.makedirs("../output", exist_ok=True)
    with open("../output/sample-instagram-official.json", "w") as f:
        json.dump(data[:3], f, indent=2)
    print("\n💾 Saved 3 sample posts to output/sample-instagram-official.json")
else:
    print("\n❌ Still getting errors:")
    print(json.dumps(data, indent=2))
