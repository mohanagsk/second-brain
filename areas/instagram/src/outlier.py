"""
Outlier Detection for Instagram Posts
Identifies high-performing content based on view metrics
"""
from typing import List, Dict, Optional
import statistics
from datetime import datetime


class OutlierDetector:
    """Detect outlier posts based on performance metrics"""
    
    def __init__(self, posts: List[Dict]):
        """
        Initialize detector with scraped posts
        
        Args:
            posts: List of post dictionaries from scraper
        """
        self.posts = posts
        self.video_posts = [p for p in posts if p.get("is_video") and p.get("views", 0) > 0]
    
    def calculate_outliers(
        self,
        metric: str = "views",
        min_threshold: float = 1.5
    ) -> List[Dict]:
        """
        Calculate outlier scores and rank posts
        
        Args:
            metric: Metric to use for outlier detection (default: "views")
            min_threshold: Minimum outlier score to include (default: 1.5x average)
        
        Returns:
            List of posts with outlier scores, sorted by score (descending)
        """
        if not self.video_posts:
            print("⚠️  No video posts with views found")
            return []
        
        # Calculate average views
        views_list = [p["views"] for p in self.video_posts]
        avg_views = statistics.mean(views_list)
        median_views = statistics.median(views_list)
        
        print(f"\n📊 Analyzing {len(self.video_posts)} video posts")
        print(f"   Average views: {avg_views:,.0f}")
        print(f"   Median views: {median_views:,.0f}")
        
        # Calculate outlier score for each post
        outlier_posts = []
        for post in self.video_posts:
            views = post["views"]
            outlier_score = views / avg_views
            
            # Only include posts above threshold
            if outlier_score >= min_threshold:
                post_with_score = post.copy()
                post_with_score["outlier_score"] = round(outlier_score, 2)
                post_with_score["avg_views"] = int(avg_views)
                post_with_score["views_above_avg"] = int(views - avg_views)
                outlier_posts.append(post_with_score)
        
        # Sort by outlier score (descending)
        outlier_posts.sort(key=lambda x: x["outlier_score"], reverse=True)
        
        print(f"   Found {len(outlier_posts)} outliers (>{min_threshold}x avg)")
        
        return outlier_posts
    
    def get_statistics(self) -> Dict:
        """Get summary statistics for all posts"""
        if not self.video_posts:
            return {"error": "No video posts with views"}
        
        views_list = [p["views"] for p in self.video_posts]
        likes_list = [p["likes"] for p in self.video_posts]
        comments_list = [p["comments"] for p in self.video_posts]
        
        engagement_rates = [
            p["engagement_rate"] 
            for p in self.video_posts 
            if p.get("engagement_rate") is not None
        ]
        
        stats = {
            "total_posts": len(self.posts),
            "video_posts": len(self.video_posts),
            "views": {
                "mean": round(statistics.mean(views_list), 0),
                "median": round(statistics.median(views_list), 0),
                "min": min(views_list),
                "max": max(views_list),
                "stdev": round(statistics.stdev(views_list), 0) if len(views_list) > 1 else 0
            },
            "likes": {
                "mean": round(statistics.mean(likes_list), 0),
                "median": round(statistics.median(likes_list), 0)
            },
            "comments": {
                "mean": round(statistics.mean(comments_list), 0),
                "median": round(statistics.median(comments_list), 0)
            }
        }
        
        if engagement_rates:
            stats["engagement_rate"] = {
                "mean": round(statistics.mean(engagement_rates), 2),
                "median": round(statistics.median(engagement_rates), 2)
            }
        
        return stats
    
    def analyze_top_performers(
        self,
        top_n: int = 10,
        min_threshold: float = 1.5
    ) -> Dict:
        """
        Analyze top performing posts for patterns
        
        Args:
            top_n: Number of top posts to analyze
            min_threshold: Minimum outlier score
        
        Returns:
            Analysis dictionary with patterns and insights
        """
        outliers = self.calculate_outliers(min_threshold=min_threshold)
        
        if not outliers:
            return {"error": "No outliers found"}
        
        top_posts = outliers[:top_n]
        
        # Extract hashtags from top posts
        all_hashtags = []
        for post in top_posts:
            all_hashtags.extend(post.get("hashtags", []))
        
        # Count hashtag frequency
        hashtag_freq = {}
        for tag in all_hashtags:
            hashtag_freq[tag] = hashtag_freq.get(tag, 0) + 1
        
        # Sort hashtags by frequency
        top_hashtags = sorted(
            hashtag_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Analyze posting times
        posting_hours = []
        for post in top_posts:
            if post.get("timestamp"):
                dt = datetime.fromtimestamp(post["timestamp"])
                posting_hours.append(dt.hour)
        
        analysis = {
            "top_posts_count": len(top_posts),
            "avg_outlier_score": round(
                statistics.mean([p["outlier_score"] for p in top_posts]), 2
            ),
            "top_hashtags": [{"tag": tag, "count": count} for tag, count in top_hashtags],
            "top_posts": [
                {
                    "url": p["url"],
                    "views": p["views"],
                    "outlier_score": p["outlier_score"],
                    "likes": p["likes"],
                    "comments": p["comments"],
                    "caption_preview": p["caption"][:100] + "..." if len(p["caption"]) > 100 else p["caption"],
                    "hashtags": p["hashtags"][:5]  # First 5 hashtags
                }
                for p in top_posts
            ]
        }
        
        if posting_hours:
            analysis["posting_hours"] = {
                "most_common": max(set(posting_hours), key=posting_hours.count),
                "distribution": posting_hours
            }
        
        return analysis
    
    def format_summary(self, outliers: List[Dict]) -> str:
        """Format outliers as a readable summary"""
        if not outliers:
            return "No outlier posts found."
        
        summary = f"\n{'='*70}\n"
        summary += f"🔥 TOP PERFORMING POSTS (Outlier Score > 1.5x)\n"
        summary += f"{'='*70}\n\n"
        
        for i, post in enumerate(outliers[:10], 1):
            summary += f"{i}. Score: {post['outlier_score']}x average\n"
            summary += f"   Views: {post['views']:,} (avg: {post['avg_views']:,})\n"
            summary += f"   Likes: {post['likes']:,} | Comments: {post['comments']:,}\n"
            summary += f"   URL: {post['url']}\n"
            
            if post.get("hashtags"):
                summary += f"   Hashtags: {' '.join(post['hashtags'][:5])}\n"
            
            caption_preview = post['caption'][:80].replace('\n', ' ')
            if len(post['caption']) > 80:
                caption_preview += "..."
            summary += f"   Caption: {caption_preview}\n"
            summary += f"\n"
        
        return summary


if __name__ == "__main__":
    # Quick test with sample data
    sample_posts = [
        {"id": 1, "is_video": True, "views": 1000, "likes": 50, "comments": 5, "caption": "Test 1", "hashtags": ["#test"], "url": "https://instagram.com/p/1"},
        {"id": 2, "is_video": True, "views": 5000, "likes": 250, "comments": 25, "caption": "Test 2", "hashtags": ["#viral"], "url": "https://instagram.com/p/2"},
        {"id": 3, "is_video": True, "views": 800, "likes": 40, "comments": 4, "caption": "Test 3", "hashtags": ["#test"], "url": "https://instagram.com/p/3"},
    ]
    
    detector = OutlierDetector(sample_posts)
    outliers = detector.calculate_outliers()
    print(detector.format_summary(outliers))
