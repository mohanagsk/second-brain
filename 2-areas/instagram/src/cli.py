#!/usr/bin/env python3
"""
Instagram Intelligence CLI
Command-line interface for scraping and analyzing Instagram creator content
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from scraper import InstagramScraper
from outlier import OutlierDetector


def main():
    parser = argparse.ArgumentParser(
        description="Instagram Intelligence: Scrape and analyze creator content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 100 posts and find outliers
  python cli.py @divy.kairoth
  
  # Scrape 50 posts without collaborations
  python cli.py @creator --max-posts 50 --no-collabs
  
  # Custom outlier threshold (2x average)
  python cli.py @creator --threshold 2.0
  
  # Save to custom location
  python cli.py @creator --output results/creator-analysis.json
        """
    )
    
    parser.add_argument(
        "username",
        help="Instagram username (with or without @)"
    )
    
    parser.add_argument(
        "--max-posts",
        type=int,
        default=100,
        help="Maximum number of posts to scrape (default: 100)"
    )
    
    parser.add_argument(
        "--no-collabs",
        action="store_true",
        help="Filter out collaboration posts"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.5,
        help="Outlier score threshold (default: 1.5x average)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file path (default: instagram-intel/output/<username>-<timestamp>.json)"
    )
    
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Show statistics only, don't calculate outliers"
    )
    
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top posts to display (default: 10)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize scraper
        print("🚀 Instagram Intelligence Tool")
        print("=" * 70)
        
        scraper = InstagramScraper()
        
        # Scrape posts
        posts = scraper.scrape_creator(
            username=args.username,
            max_posts=args.max_posts,
            filter_collaborations=args.no_collabs
        )
        
        if not posts:
            print("❌ No posts found")
            sys.exit(1)
        
        # Initialize detector
        detector = OutlierDetector(posts)
        
        # Get statistics
        print("\n" + "=" * 70)
        print("📊 CONTENT STATISTICS")
        print("=" * 70)
        
        stats = detector.get_statistics()
        
        if "error" in stats:
            print(f"❌ {stats['error']}")
            sys.exit(1)
        
        print(f"\nTotal posts scraped: {stats['total_posts']}")
        print(f"Video posts with views: {stats['video_posts']}")
        
        print(f"\n📺 Views:")
        print(f"   Mean: {stats['views']['mean']:,.0f}")
        print(f"   Median: {stats['views']['median']:,.0f}")
        print(f"   Range: {stats['views']['min']:,.0f} - {stats['views']['max']:,.0f}")
        print(f"   Std Dev: {stats['views']['stdev']:,.0f}")
        
        print(f"\n❤️  Likes:")
        print(f"   Mean: {stats['likes']['mean']:,.0f}")
        print(f"   Median: {stats['likes']['median']:,.0f}")
        
        print(f"\n💬 Comments:")
        print(f"   Mean: {stats['comments']['mean']:,.0f}")
        print(f"   Median: {stats['comments']['median']:,.0f}")
        
        if "engagement_rate" in stats:
            print(f"\n🔥 Engagement Rate:")
            print(f"   Mean: {stats['engagement_rate']['mean']}%")
            print(f"   Median: {stats['engagement_rate']['median']}%")
        
        # Calculate outliers (unless stats-only mode)
        outliers = []
        if not args.stats_only:
            outliers = detector.calculate_outliers(min_threshold=args.threshold)
            
            if outliers:
                print(detector.format_summary(outliers[:args.top]))
                
                # Analyze top performers
                print("=" * 70)
                print("🎯 TOP PERFORMER ANALYSIS")
                print("=" * 70)
                
                analysis = detector.analyze_top_performers(
                    top_n=args.top,
                    min_threshold=args.threshold
                )
                
                print(f"\nTop {analysis['top_posts_count']} posts:")
                print(f"   Avg outlier score: {analysis['avg_outlier_score']}x")
                
                if analysis.get("top_hashtags"):
                    print(f"\n📌 Most common hashtags in top posts:")
                    for tag_data in analysis["top_hashtags"][:5]:
                        print(f"   {tag_data['tag']}: {tag_data['count']} times")
                
                if analysis.get("posting_hours"):
                    print(f"\n⏰ Most common posting hour: {analysis['posting_hours']['most_common']}:00")
        
        # Prepare output data
        output_data = {
            "username": args.username.lstrip("@"),
            "scraped_at": datetime.now().isoformat(),
            "config": {
                "max_posts": args.max_posts,
                "filter_collaborations": args.no_collabs,
                "outlier_threshold": args.threshold
            },
            "statistics": stats,
            "outliers": outliers if not args.stats_only else [],
            "all_posts": posts
        }
        
        # Save to file
        if args.output:
            output_path = Path(args.output)
        else:
            # Default output location
            output_dir = Path("instagram-intel/output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            username_clean = args.username.lstrip("@")
            output_path = output_dir / f"{username_clean}-{timestamp}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print("\n" + "=" * 70)
        print(f"💾 Results saved to: {output_path}")
        print("=" * 70)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
