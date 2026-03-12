#!/usr/bin/env python3
"""
Instagram Daily Monitor
Scrapes competitor profiles and detects outliers
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from apify_scraper import run_actor, analyze_reels, DATA_DIR

# Competitors to monitor
COMPETITORS = [
    "vedikabhaia",
    "jaykapoor.24",
]

# Your profile for comparison
MY_PROFILE = "divy.kairoth"

# State file to track what we've already reported
STATE_FILE = DATA_DIR / "monitor_state.json"


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"reported_urls": [], "last_check": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def find_new_outliers(analysis: dict, state: dict, threshold: float = 2.0) -> list:
    """Find outliers that haven't been reported yet"""
    new_outliers = []
    reported_urls = set(state.get("reported_urls", []))
    
    for reel in analysis.get("reels", []):
        if reel["outlier_score"] >= threshold and reel["url"] not in reported_urls:
            new_outliers.append(reel)
    
    return new_outliers


def format_outlier_alert(competitor: str, outliers: list, avg_plays: int) -> str:
    """Format alert message for Telegram"""
    if not outliers:
        return ""
    
    lines = [f"🔥 **NEW OUTLIERS from @{competitor}**"]
    lines.append(f"(Avg plays: {avg_plays:,})\n")
    
    for reel in outliers[:3]:  # Max 3 per alert
        score = reel['outlier_score']
        plays = reel['plays']
        caption = (reel.get('caption') or '')[:100]
        url = reel['url']
        
        lines.append(f"**{plays:,} plays ({score}x avg)**")
        lines.append(f"{caption}...")
        lines.append(f"🔗 {url}\n")
    
    return "\n".join(lines)


def run_daily_check():
    """Run daily competitor check"""
    state = load_state()
    alerts = []
    
    for competitor in COMPETITORS:
        print(f"\n📱 Checking @{competitor}...")
        
        reels = run_actor([competitor], results_limit=20)
        if not reels:
            print(f"⚠️ Failed to scrape @{competitor}")
            continue
        
        analysis = analyze_reels(reels, competitor)
        
        # Save today's data
        today = datetime.now().strftime('%Y%m%d')
        analysis_path = DATA_DIR / f"{competitor}_analysis_{today}.json"
        with open(analysis_path, "w") as f:
            json.dump(analysis, f, indent=2)
        
        # Find new outliers
        new_outliers = find_new_outliers(analysis, state, threshold=2.0)
        
        if new_outliers:
            alert = format_outlier_alert(
                competitor, 
                new_outliers, 
                analysis["avg_plays"]
            )
            alerts.append(alert)
            
            # Mark as reported
            for reel in new_outliers:
                state["reported_urls"].append(reel["url"])
    
    # Keep only last 500 reported URLs
    state["reported_urls"] = state["reported_urls"][-500:]
    state["last_check"] = datetime.utcnow().isoformat()
    save_state(state)
    
    return alerts


def generate_weekly_digest() -> str:
    """Generate weekly comparison digest"""
    # Load latest analysis for each profile
    profiles = [MY_PROFILE] + COMPETITORS
    data = {}
    
    for profile in profiles:
        # Find most recent analysis file
        files = sorted(DATA_DIR.glob(f"{profile}_analysis_*.json"), reverse=True)
        if files:
            with open(files[0]) as f:
                data[profile] = json.load(f)
    
    if not data:
        return "No data available for digest"
    
    lines = ["📊 **WEEKLY INSTAGRAM DIGEST**\n"]
    
    # Comparison table
    lines.append("| Profile | Avg Plays | Outliers | Top Reel |")
    lines.append("|---------|-----------|----------|----------|")
    
    for profile, analysis in data.items():
        avg = analysis.get("avg_plays", 0)
        outliers = analysis.get("outliers_count", 0)
        top_plays = analysis.get("reels", [{}])[0].get("plays", 0) if analysis.get("reels") else 0
        
        marker = "📍" if profile == MY_PROFILE else ""
        lines.append(f"| @{profile} {marker} | {avg:,} | {outliers} | {top_plays:,} |")
    
    # Top outliers across all competitors
    all_outliers = []
    for profile, analysis in data.items():
        if profile == MY_PROFILE:
            continue
        for reel in analysis.get("outliers", []):
            reel["_profile"] = profile
            all_outliers.append(reel)
    
    all_outliers.sort(key=lambda x: x["plays"], reverse=True)
    
    if all_outliers:
        lines.append("\n**🔥 TOP COMPETITOR OUTLIERS THIS WEEK:**")
        for reel in all_outliers[:5]:
            lines.append(f"\n• @{reel['_profile']}: {reel['plays']:,} plays ({reel['outlier_score']}x)")
            lines.append(f"  {(reel.get('caption') or '')[:80]}...")
            lines.append(f"  {reel['url']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "digest":
        print(generate_weekly_digest())
    else:
        alerts = run_daily_check()
        if alerts:
            print("\n" + "="*50)
            print("ALERTS TO SEND:")
            print("="*50)
            for alert in alerts:
                print(alert)
        else:
            print("\n✅ No new outliers found")
