"""
Instagram Scraper using Apify API
Uses apidojo/instagram-scraper to fetch posts from Instagram creators
"""
import os
import time
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv


class InstagramScraper:
    """Wrapper for Apify Instagram scraper API"""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize scraper with Apify API token
        
        Args:
            api_token: Apify API token (if None, loads from env)
        """
        if api_token is None:
            # Load from credentials/apify-creds.env
            creds_path = os.path.expanduser("~/.openclaw/workspace/credentials/apify-creds.env")
            load_dotenv(creds_path)
            api_token = os.getenv("APIFY_TOKEN")
        
        if not api_token:
            raise ValueError("APIFY_TOKEN not found. Set it in credentials/apify-creds.env")
        
        self.api_token = api_token
        self.actor_id = "apify~instagram-scraper"
        self.base_url = "https://api.apify.com/v2"
    
    def scrape_creator(
        self,
        username: str,
        max_posts: int = 100,
        filter_collaborations: bool = False
    ) -> List[Dict]:
        """
        Scrape posts from an Instagram creator
        
        Args:
            username: Instagram username (with or without @)
            max_posts: Maximum number of posts to fetch (default: 100)
            filter_collaborations: Filter out collaborative posts (default: False)
        
        Returns:
            List of post dictionaries with extracted metrics
        """
        # Clean username
        username = username.lstrip("@")
        
        print(f"🔍 Scraping @{username} for up to {max_posts} posts...")
        
        # Prepare actor input
        run_input = {
            "username": [username],
            "resultsLimit": max_posts,
            "resultsType": "posts",
            "searchType": "user",
            "searchLimit": 1,
            "addParentData": False
        }
        
        # Start actor run
        run_url = f"{self.base_url}/acts/{self.actor_id}/runs"
        headers = {"Content-Type": "application/json"}
        params = {"token": self.api_token}
        
        print("⏳ Starting Apify actor run...")
        response = requests.post(
            run_url,
            json=run_input,
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        run_data = response.json()["data"]
        run_id = run_data["id"]
        
        # Wait for run to complete
        print(f"⏳ Run ID: {run_id} - waiting for completion...")
        dataset_id = self._wait_for_run(run_id)
        
        # Fetch results from dataset
        print("📥 Fetching results from dataset...")
        posts = self._fetch_dataset(dataset_id)
        
        # Extract and transform post data
        print(f"📊 Processing {len(posts)} posts...")
        extracted_posts = []
        
        for post in posts:
            # Skip collaborations if filter enabled
            if filter_collaborations and self._is_collaboration(post):
                continue
            
            extracted = self._extract_post_data(post)
            extracted_posts.append(extracted)
        
        print(f"✅ Successfully scraped {len(extracted_posts)} posts")
        return extracted_posts
    
    def _wait_for_run(self, run_id: str, max_wait: int = 300) -> str:
        """Wait for actor run to complete and return dataset ID"""
        run_url = f"{self.base_url}/actor-runs/{run_id}"
        params = {"token": self.api_token}
        
        start_time = time.time()
        while True:
            if time.time() - start_time > max_wait:
                raise TimeoutError(f"Run {run_id} did not complete in {max_wait}s")
            
            response = requests.get(run_url, params=params, timeout=30)
            response.raise_for_status()
            
            run_data = response.json()["data"]
            status = run_data["status"]
            
            if status == "SUCCEEDED":
                dataset_id = run_data["defaultDatasetId"]
                print(f"✅ Run completed successfully")
                return dataset_id
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                raise RuntimeError(f"Run {run_id} {status}")
            
            # Still running
            print(f"⏳ Status: {status}... waiting")
            time.sleep(5)
    
    def _fetch_dataset(self, dataset_id: str) -> List[Dict]:
        """Fetch all items from dataset"""
        dataset_url = f"{self.base_url}/datasets/{dataset_id}/items"
        params = {"token": self.api_token, "format": "json"}
        
        response = requests.get(dataset_url, params=params, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def _is_collaboration(self, post: Dict) -> bool:
        """Check if post is a collaboration"""
        # Check for coauthor_producers field
        if post.get("coauthor_producers"):
            return True
        
        # Check caption for collaboration indicators
        caption = post.get("caption", {}).get("text", "").lower()
        collab_keywords = ["collab", "collaboration", "with @", "ft.", "featuring"]
        return any(keyword in caption for keyword in collab_keywords)
    
    def _extract_post_data(self, post: Dict) -> Dict:
        """Extract relevant metrics from raw post data"""
        # Get caption data
        caption_data = post.get("caption", {})
        caption_text = caption_data.get("text", "")
        
        # Extract hashtags from caption
        hashtags = []
        if caption_text:
            hashtags = [word for word in caption_text.split() if word.startswith("#")]
        
        # Get engagement metrics
        like_count = post.get("like_count", 0) or post.get("likeCount", 0)
        comment_count = post.get("comment_count", 0) or post.get("commentsCount", 0)
        
        # Views/plays for video content
        plays = post.get("play_count", 0) or post.get("video_view_count", 0) or 0
        
        # Engagement rate calculation (likes + comments) / views (if available)
        if plays > 0:
            engagement_rate = ((like_count + comment_count) / plays) * 100
        else:
            # For photo posts, we can't calculate true engagement rate without follower count
            engagement_rate = None
        
        # Get timestamp
        timestamp = post.get("taken_at", 0) or post.get("takenAt", 0)
        
        # Get video URL if available
        video_url = None
        if post.get("video_url"):
            video_url = post.get("video_url")
        elif post.get("video_versions"):
            video_url = post["video_versions"][0].get("url")
        
        # Get post URL
        shortcode = post.get("code", "") or post.get("shortCode", "")
        post_url = f"https://www.instagram.com/p/{shortcode}/" if shortcode else None
        
        return {
            "id": post.get("id") or post.get("pk"),
            "shortcode": shortcode,
            "url": post_url,
            "timestamp": timestamp,
            "caption": caption_text[:500],  # Truncate long captions
            "hashtags": hashtags,
            "likes": like_count,
            "comments": comment_count,
            "views": plays,
            "engagement_rate": round(engagement_rate, 2) if engagement_rate else None,
            "video_url": video_url,
            "is_video": post.get("media_type") == 2 or bool(video_url),
            "type": post.get("product_type", "unknown")
        }


if __name__ == "__main__":
    # Quick test
    scraper = InstagramScraper()
    posts = scraper.scrape_creator("divy.kairoth", max_posts=10)
    print(f"\nFetched {len(posts)} posts")
    if posts:
        print(f"Sample post: {posts[0]}")
