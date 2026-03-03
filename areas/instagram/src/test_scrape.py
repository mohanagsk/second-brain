#!/usr/bin/env python3
"""Quick test to see what data we get from Instagram scraper"""
import json
from scraper import InstagramScraper

scraper = InstagramScraper()

# Try with different settings - get posts from profile
print("Testing with resultsType='posts'...")
try:
    posts = scraper.scrape_creator("divy.kairoth", max_posts=100)
    print(f"Got {len(posts)} posts")
    
    if posts:
        print("\nFirst post data:")
        print(json.dumps(posts[0], indent=2))
        
        # Save raw data for inspection
        with open("../output/test-divy-raw.json", "w") as f:
            json.dump(posts, f, indent=2)
        print("\n✅ Saved to output/test-divy-raw.json")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
