import requests
import json
import time
import sys

APIFY_TOKEN = "apify_api_dfMIGRu30RaKzqraUAlII64TjWzbge11c6E6"

# Start the Instagram Profile Scraper
actor_id = "apify/instagram-profile-scraper"
run_input = {
    "usernames": ["divy.kairoth"],
    "resultsLimit": 50
}

print("Starting Apify Instagram scraper...")
response = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}",
    json=run_input
)

if response.status_code != 201:
    print(f"Error starting actor: {response.text}")
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

# Extract video URLs
videos = []
for item in results:
    if "latestPosts" in item:
        for post in item["latestPosts"]:
            if post.get("type") == "Video":
                videos.append({
                    "url": post.get("videoUrl"),
                    "displayUrl": post.get("displayUrl"),
                    "caption": post.get("caption", ""),
                    "likesCount": post.get("likesCount", 0),
                    "commentsCount": post.get("commentsCount", 0)
                })

# Save to JSON
with open("reels_data.json", "w") as f:
    json.dump(videos, f, indent=2)

print(f"Found {len(videos)} videos")
print(f"Saved to reels_data.json")
