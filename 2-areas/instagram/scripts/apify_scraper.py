#!/usr/bin/env python3
"""
Instagram Reels Scraper using Apify
Scrapes profile reels with full metadata for analysis
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Load Apify token
CREDS_PATH = Path.home() / ".openclaw/workspace/credentials/apify-creds.env"
with open(CREDS_PATH) as f:
    for line in f:
        if line.startswith("APIFY_TOKEN="):
            APIFY_TOKEN = line.strip().split("=", 1)[1]
            break

BASE_URL = "https://api.apify.com/v2"
ACTOR_ID = "apify~instagram-reel-scraper"

DATA_DIR = Path.home() / ".openclaw/workspace/instagram-intel/data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_actor(usernames: list, results_limit: int = 100) -> dict:
    """Run the Instagram Reel Scraper actor"""
    
    # Prepare input - handle both usernames and full URLs
    direct_urls = []
    profile_usernames = []
    
    for u in usernames:
        if "instagram.com/reel/" in u or "instagram.com/p/" in u:
            direct_urls.append(u)
        elif "instagram.com/" in u:
            # Extract username from URL
            parts = u.rstrip("/").split("/")
            username = parts[-2] if parts[-1] == "reels" else parts[-1]
            profile_usernames.append(username.lstrip("@"))
        else:
            profile_usernames.append(u.lstrip("@"))
    
    run_input = {
        "resultsLimit": results_limit,
    }
    
    # The actor expects 'username' as an array
    if profile_usernames:
        run_input["username"] = profile_usernames
    if direct_urls:
        run_input["directUrls"] = direct_urls
    
    print(f"🚀 Starting Apify actor with input: {json.dumps(run_input, indent=2)}")
    
    # Start the actor run
    response = requests.post(
        f"{BASE_URL}/acts/{ACTOR_ID}/runs",
        params={"token": APIFY_TOKEN},
        json=run_input,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to start actor: {response.status_code}")
        print(response.text)
        return None
    
    run_data = response.json()["data"]
    run_id = run_data["id"]
    print(f"✅ Actor started. Run ID: {run_id}")
    
    # Poll for completion
    while True:
        status_response = requests.get(
            f"{BASE_URL}/actor-runs/{run_id}",
            params={"token": APIFY_TOKEN}
        )
        status = status_response.json()["data"]["status"]
        print(f"⏳ Status: {status}")
        
        if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            break
        
        time.sleep(5)
    
    if status != "SUCCEEDED":
        print(f"❌ Actor run failed with status: {status}")
        return None
    
    # Get the dataset
    dataset_id = status_response.json()["data"]["defaultDatasetId"]
    
    items_response = requests.get(
        f"{BASE_URL}/datasets/{dataset_id}/items",
        params={"token": APIFY_TOKEN, "format": "json"}
    )
    
    return items_response.json()


def analyze_reels(reels: list, username: str) -> dict:
    """Analyze reels and calculate outlier scores"""
    
    if not reels:
        return {"error": "No reels found"}
    
    # Extract metrics
    processed = []
    for reel in reels:
        plays = reel.get("playsCount") or reel.get("videoPlayCount") or 0
        likes = reel.get("likesCount", 0)
        comments = reel.get("commentsCount", 0)
        
        processed.append({
            "id": reel.get("id"),
            "shortCode": reel.get("shortCode"),
            "url": reel.get("url"),
            "caption": (reel.get("caption") or "")[:200],
            "hashtags": reel.get("hashtags", []),
            "plays": plays,
            "likes": likes,
            "comments": comments,
            "engagement": likes + comments,
            "timestamp": reel.get("timestamp"),
            "duration": reel.get("videoDuration"),
            "transcript": reel.get("transcript"),
            "videoUrl": reel.get("videoUrl"),
        })
    
    # Calculate averages
    total_plays = sum(r["plays"] for r in processed)
    total_engagement = sum(r["engagement"] for r in processed)
    avg_plays = total_plays / len(processed) if processed else 0
    avg_engagement = total_engagement / len(processed) if processed else 0
    
    # Calculate outlier scores
    for reel in processed:
        reel["outlier_score"] = round(reel["plays"] / avg_plays, 2) if avg_plays > 0 else 0
        reel["engagement_rate"] = round((reel["engagement"] / reel["plays"] * 100), 2) if reel["plays"] > 0 else 0
    
    # Sort by plays (descending)
    processed.sort(key=lambda x: x["plays"], reverse=True)
    
    # Identify outliers (>2x average)
    outliers = [r for r in processed if r["outlier_score"] >= 2.0]
    underperformers = [r for r in processed if r["outlier_score"] < 0.5]
    
    return {
        "username": username,
        "scraped_at": datetime.utcnow().isoformat(),
        "total_reels": len(processed),
        "avg_plays": round(avg_plays),
        "avg_engagement": round(avg_engagement),
        "outliers_count": len(outliers),
        "underperformers_count": len(underperformers),
        "reels": processed,
        "outliers": outliers,
        "underperformers": underperformers,
    }


def scrape_profile(username: str, limit: int = 100) -> dict:
    """Scrape a single profile and save results"""
    
    print(f"\n{'='*50}")
    print(f"📱 Scraping @{username}")
    print(f"{'='*50}\n")
    
    reels = run_actor([username], results_limit=limit)
    
    if not reels:
        return {"error": f"Failed to scrape @{username}"}
    
    analysis = analyze_reels(reels, username)
    
    # Save raw data
    raw_path = DATA_DIR / f"{username}_raw_{datetime.now().strftime('%Y%m%d')}.json"
    with open(raw_path, "w") as f:
        json.dump(reels, f, indent=2)
    print(f"💾 Raw data saved: {raw_path}")
    
    # Save analysis
    analysis_path = DATA_DIR / f"{username}_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"📊 Analysis saved: {analysis_path}")
    
    return analysis


def print_report(analysis: dict):
    """Print a formatted report"""
    
    print(f"\n{'='*60}")
    print(f"📊 REPORT: @{analysis['username']}")
    print(f"{'='*60}")
    print(f"Total Reels: {analysis['total_reels']}")
    print(f"Average Plays: {analysis['avg_plays']:,}")
    print(f"Average Engagement: {analysis['avg_engagement']:,}")
    print(f"Outliers (>2x avg): {analysis['outliers_count']}")
    print(f"Underperformers (<0.5x avg): {analysis['underperformers_count']}")
    
    print(f"\n🔥 TOP 10 BY VIEWS:")
    print("-" * 60)
    for i, reel in enumerate(analysis['reels'][:10], 1):
        print(f"{i}. {reel['plays']:>10,} plays | {reel['outlier_score']}x | {reel['caption'][:50]}...")
        print(f"   URL: {reel['url']}")
    
    if analysis['outliers']:
        print(f"\n⭐ OUTLIERS (>2x average):")
        print("-" * 60)
        for reel in analysis['outliers'][:5]:
            print(f"• {reel['plays']:,} plays ({reel['outlier_score']}x avg)")
            print(f"  {reel['caption'][:80]}...")
            print(f"  {reel['url']}\n")
    
    if analysis['underperformers']:
        print(f"\n📉 UNDERPERFORMERS (<0.5x average):")
        print("-" * 60)
        for reel in analysis['underperformers'][:5]:
            print(f"• {reel['plays']:,} plays ({reel['outlier_score']}x avg)")
            print(f"  {reel['caption'][:80]}...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python apify_scraper.py <username_or_url> [limit]")
        print("Example: python apify_scraper.py divy.kairoth 50")
        sys.exit(1)
    
    username = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    analysis = scrape_profile(username, limit)
    
    if "error" not in analysis:
        print_report(analysis)
