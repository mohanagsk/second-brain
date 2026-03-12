#!/usr/bin/env python3
"""Debug script to see raw Apify response"""
import os
import json
import time
import requests
from dotenv import load_dotenv

# Load credentials
creds_path = os.path.expanduser("~/.openclaw/workspace/credentials/apify-creds.env")
load_dotenv(creds_path)
api_token = os.getenv("APIFY_TOKEN")

# Actor config
actor_id = "apify~instagram-scraper"
base_url = "https://api.apify.com/v2"

# Prepare input - try to get profile data
run_input = {
    "username": ["divy.kairoth"],
    "resultsLimit": 100,
    "resultsType": "posts",  # or "details" for profile info
    "searchType": "user",
    "searchLimit": 1,
    "addParentData": False
}

print("Input config:")
print(json.dumps(run_input, indent=2))

# Start run
run_url = f"{base_url}/acts/{actor_id}/runs"
headers = {"Content-Type": "application/json"}
params = {"token": api_token}

print("\nStarting actor run...")
response = requests.post(run_url, json=run_input, headers=headers, params=params, timeout=30)
response.raise_for_status()

run_data = response.json()["data"]
run_id = run_data["id"]
print(f"Run ID: {run_id}")

# Wait for completion
print("\nWaiting for completion...")
run_url = f"{base_url}/actor-runs/{run_id}"
while True:
    response = requests.get(run_url, params=params, timeout=30)
    response.raise_for_status()
    
    run_data = response.json()["data"]
    status = run_data["status"]
    
    if status == "SUCCEEDED":
        print("✅ Run completed")
        break
    elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
        print(f"❌ Run {status}")
        print(json.dumps(run_data, indent=2))
        exit(1)
    
    print(f"Status: {status}...")
    time.sleep(3)

# Get dataset
dataset_id = run_data["defaultDatasetId"]
dataset_url = f"{base_url}/datasets/{dataset_id}/items"
params = {"token": api_token, "format": "json"}

print(f"\nFetching dataset {dataset_id}...")
response = requests.get(dataset_url, params=params, timeout=60)
response.raise_for_status()

data = response.json()

print(f"\nGot {len(data)} items")
print("\nRaw response:")
print(json.dumps(data, indent=2))

# Save to file
os.makedirs("../output", exist_ok=True)
with open("../output/raw-apify-response.json", "w") as f:
    json.dump(data, f, indent=2)

print("\n✅ Saved to output/raw-apify-response.json")
