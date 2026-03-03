import requests
import json
import time
import sys

APIFY_TOKEN = "apify_api_dfMIGRu30RaKzqraUAlII64TjWzbge11c6E6"

# Try the Instagram Reels Scraper
actor_id = "apify/instagram-reel-scraper"
run_input = {
    "username": ["divy.kairoth"],
    "resultsLimit": 20
}

print("Starting Apify Instagram Reels scraper...")
response = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}",
    json=run_input
)

if response.status_code != 201:
    print(f"Error: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Try alternative: direct URLs approach
    print("\nTrying direct URL approach...")
    
    # For now, let's use some sample Instagram reel URLs from @divy.kairoth
    # We'll need to manually construct or use a web scraper
    print("Note: Will need to use alternative method")
    sys.exit(1)

run_data = response.json()["data"]
run_id = run_data["id"]
print(f"Run started: {run_id}")

# Poll for completion
while True:
    status_response = requests.get(
        f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}?token={APIFY_TOKEN}"
    )
    status = status_response.json()["data"]["status"]
    print(f"Status: {status}")
    
    if status in ["SUCCEEDED", "FAILED", "ABORTED"]:
        break
    
    time.sleep(5)

if status != "SUCCEEDED":
    print(f"Run failed with status: {status}")
    sys.exit(1)

# Get results
dataset_id = run_data["defaultDatasetId"]
results_response = requests.get(
    f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
)

results = results_response.json()
with open("reels_data.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Found {len(results)} reels")
