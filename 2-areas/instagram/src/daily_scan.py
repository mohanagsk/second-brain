#!/usr/bin/env python3
"""
daily_scan.py - ContentRadar Daily Automation
Orchestrates the entire pipeline: scrape → detect → download → analyze → report
"""
import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import requests
from statistics import mean, stdev

# Import our modules
from media import MediaProcessor
from transcribe import Transcriber
from analyze import ContentAnalyzer


class ContentRadar:
    """Main orchestrator for daily content scanning"""
    
    def __init__(self, config_path: str = "config/watchlist.yaml"):
        """Initialize ContentRadar with configuration"""
        self.config = self.load_config(config_path)
        self.workspace = Path(__file__).parent.parent
        self.data_dir = self.workspace / "data"
        self.swipe_dir = self.data_dir / "swipe_files"
        self.reports_dir = self.data_dir / "reports"
        self.downloads_dir = self.data_dir / "downloads"
        
        # Create directories
        for dir_path in [self.data_dir, self.swipe_dir, self.reports_dir, self.downloads_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load credentials
        self.load_credentials()
        
        # Initialize components
        self.media_processor = MediaProcessor(output_dir=str(self.data_dir / "processed"))
        self.transcriber = Transcriber(api_key=self.groq_key)
        self.analyzer = ContentAnalyzer(
            claude_api_key=self.claude_key,
            gemini_api_key=self.gemini_key
        )
        
        print("✅ ContentRadar initialized")
    
    def load_config(self, config_path: str) -> dict:
        """Load watchlist configuration"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def load_credentials(self):
        """Load API credentials from workspace"""
        creds_dir = Path.home() / ".openclaw/workspace/credentials"
        
        # Apify
        apify_file = creds_dir / "apify-creds.env"
        if apify_file.exists():
            with open(apify_file) as f:
                for line in f:
                    if line.startswith("APIFY_TOKEN="):
                        self.apify_token = line.split("=", 1)[1].strip()
        
        # Gemini
        gemini_file = creds_dir / "gemini-key.env"
        if gemini_file.exists():
            with open(gemini_file) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        self.gemini_key = line.split("=", 1)[1].strip()
        
        # Claude (from env)
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.claude_key:
            print("⚠️  ANTHROPIC_API_KEY not found in environment")
        
        # Groq (from env)
        self.groq_key = os.getenv("GROQ_API_KEY")
        if not self.groq_key:
            print("⚠️  GROQ_API_KEY not found in environment")
    
    def scrape_posts(self, username: str, limit: int = 100) -> List[Dict]:
        """
        Scrape Instagram posts using Apify
        
        Args:
            username: Instagram username (without @)
            limit: Number of posts to scrape
            
        Returns:
            List of post data dictionaries
        """
        print(f"🔍 Scraping @{username} (last {limit} posts)...")
        
        # Apify Instagram Profile Scraper actor
        actor_id = "apify/instagram-profile-scraper"
        
        # Prepare input
        run_input = {
            "usernames": [username],
            "resultsLimit": limit,
            "resultsType": "posts"
        }
        
        headers = {
            "Authorization": f"Bearer {self.apify_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Start the actor run
            response = requests.post(
                f"https://api.apify.com/v2/acts/{actor_id}/runs",
                headers=headers,
                json=run_input,
                timeout=30
            )
            response.raise_for_status()
            run_data = response.json()
            run_id = run_data['data']['id']
            
            print(f"  ⏳ Run started: {run_id}")
            
            # Wait for completion (poll every 10 seconds)
            import time
            max_wait = 600  # 10 minutes
            elapsed = 0
            
            while elapsed < max_wait:
                time.sleep(10)
                elapsed += 10
                
                status_response = requests.get(
                    f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}",
                    headers=headers
                )
                status_data = status_response.json()
                status = status_data['data']['status']
                
                if status == "SUCCEEDED":
                    print(f"  ✅ Scraping completed")
                    break
                elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                    raise RuntimeError(f"Apify run failed with status: {status}")
                
                print(f"  ⏳ Status: {status} ({elapsed}s elapsed)")
            
            # Get results
            dataset_id = status_data['data']['defaultDatasetId']
            results_response = requests.get(
                f"https://api.apify.com/v2/datasets/{dataset_id}/items",
                headers=headers
            )
            results = results_response.json()
            
            # Parse posts
            posts = []
            for item in results:
                if item.get('type') == 'Post':
                    posts.append({
                        'username': username,
                        'url': item.get('url'),
                        'caption': item.get('caption', ''),
                        'likes': item.get('likesCount', 0),
                        'comments': item.get('commentsCount', 0),
                        'views': item.get('videoViewCount', 0),
                        'timestamp': item.get('timestamp'),
                        'video_url': item.get('videoUrl'),
                        'is_video': item.get('type') == 'Video' or bool(item.get('videoUrl'))
                    })
            
            print(f"  📊 Found {len(posts)} posts")
            return posts
            
        except Exception as e:
            print(f"  ❌ Scraping failed: {e}")
            return []
    
    def detect_outliers(self, posts: List[Dict]) -> List[Dict]:
        """
        Detect outlier posts (>3x average engagement)
        
        Args:
            posts: List of post data
            
        Returns:
            List of outlier posts with outlier_factor added
        """
        if not posts:
            return []
        
        # Calculate engagement scores
        engagements = [p['likes'] + (p['comments'] * 2) for p in posts]
        avg_engagement = mean(engagements)
        
        threshold = self.config['thresholds']['outlier_multiplier']
        major_threshold = self.config['thresholds']['major_outlier_multiplier']
        
        outliers = []
        for i, post in enumerate(posts):
            engagement = engagements[i]
            factor = engagement / avg_engagement if avg_engagement > 0 else 0
            
            if factor >= threshold:
                post['outlier_factor'] = factor
                post['is_major_outlier'] = factor >= major_threshold
                outliers.append(post)
        
        print(f"🎯 Found {len(outliers)} outliers (avg engagement: {avg_engagement:.0f})")
        for outlier in outliers:
            emoji = "🚨" if outlier['is_major_outlier'] else "📈"
            print(f"  {emoji} {outlier['outlier_factor']:.1f}x - {outlier['likes']:,} likes")
        
        return sorted(outliers, key=lambda x: x['outlier_factor'], reverse=True)
    
    def download_video(self, url: str, output_name: str) -> str:
        """
        Download video using yt-dlp
        
        Args:
            url: Video URL
            output_name: Output filename (without extension)
            
        Returns:
            Path to downloaded video
        """
        output_path = self.downloads_dir / f"{output_name}.mp4"
        
        cmd = [
            "yt-dlp",
            "-f", "best",
            "-o", str(output_path),
            url
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  ✅ Downloaded: {output_path.name}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Download failed: {e}")
            return None
    
    def process_outlier(self, post: Dict, index: int) -> Dict:
        """
        Process a single outlier post through the full pipeline
        
        Args:
            post: Post data dictionary
            index: Index for naming files
            
        Returns:
            Dictionary with processing results
        """
        username = post['username']
        print(f"\n{'='*60}")
        print(f"Processing outlier #{index + 1}: @{username}")
        print(f"Factor: {post['outlier_factor']:.1f}x | Likes: {post['likes']:,}")
        print(f"{'='*60}")
        
        result = {
            'post': post,
            'success': False
        }
        
        # 1. Download video
        if not post.get('video_url'):
            print("  ⚠️  No video URL found, skipping")
            return result
        
        video_name = f"{username}_{index + 1}"
        video_path = self.download_video(post['video_url'], video_name)
        
        if not video_path:
            return result
        
        # 2. Extract audio
        print("  🎵 Extracting audio...")
        try:
            audio_path = self.media_processor.extract_audio(video_path, f"{video_name}_audio.mp3")
        except Exception as e:
            print(f"  ❌ Audio extraction failed: {e}")
            return result
        
        # 3. Extract frames
        print("  🎬 Extracting frames...")
        try:
            frame_paths = self.media_processor.extract_frames(video_path, num_frames=5, output_prefix=video_name)
            print(f"  ✅ Extracted {len(frame_paths)} frames")
        except Exception as e:
            print(f"  ❌ Frame extraction failed: {e}")
            frame_paths = []
        
        # 4. Transcribe audio
        print("  🎙️  Transcribing audio...")
        try:
            transcription_result = self.transcriber.transcribe(audio_path, language="en")
            transcription = transcription_result['text']
            print(f"  ✅ Transcribed ({transcription_result['duration']:.1f}s)")
        except Exception as e:
            print(f"  ❌ Transcription failed: {e}")
            transcription = "[Transcription failed]"
        
        # 5. Analyze content (Claude)
        print("  🧠 Analyzing content (Claude)...")
        try:
            claude_analysis = self.analyzer.analyze_content_claude(post, transcription)
            if 'error' in claude_analysis:
                print(f"  ⚠️  Claude analysis error: {claude_analysis['error']}")
        except Exception as e:
            print(f"  ❌ Claude analysis failed: {e}")
            claude_analysis = {'error': str(e)}
        
        # 6. Analyze visuals (Gemini)
        print("  🎨 Analyzing visuals (Gemini)...")
        try:
            gemini_analysis = self.analyzer.analyze_visuals_gemini(frame_paths, post)
            if 'error' in gemini_analysis:
                print(f"  ⚠️  Gemini analysis error: {gemini_analysis['error']}")
        except Exception as e:
            print(f"  ❌ Gemini analysis failed: {e}")
            gemini_analysis = {'error': str(e)}
        
        # 7. Generate swipe file entry
        print("  📝 Generating swipe file...")
        try:
            swipe_entry = self.analyzer.generate_swipe_file_entry(
                post, claude_analysis, gemini_analysis, transcription
            )
            
            # Save to swipe file
            timestamp = datetime.now().strftime("%Y%m%d")
            swipe_file = self.swipe_dir / f"{timestamp}_{username}_{index + 1}.md"
            with open(swipe_file, 'w') as f:
                f.write(swipe_entry)
            print(f"  ✅ Saved: {swipe_file.name}")
            
            result['swipe_file'] = str(swipe_file)
        except Exception as e:
            print(f"  ❌ Swipe file generation failed: {e}")
        
        result['success'] = True
        result['transcription'] = transcription
        result['claude_analysis'] = claude_analysis
        result['gemini_analysis'] = gemini_analysis
        
        return result
    
    def generate_summary_report(self, all_results: List[Dict]) -> str:
        """Generate summary report of the scan"""
        report = []
        report.append("# ContentRadar Daily Scan Report")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Creators Scanned:** {len(self.config['creators'])}")
        report.append("")
        
        total_outliers = sum(1 for r in all_results if r.get('success'))
        major_outliers = sum(1 for r in all_results if r.get('post', {}).get('is_major_outlier'))
        
        report.append(f"## 📊 Summary")
        report.append(f"- **Total Outliers Found:** {total_outliers}")
        report.append(f"- **Major Outliers (>10x):** {major_outliers}")
        report.append("")
        
        report.append("## 🎯 Top Performers")
        for i, result in enumerate(all_results[:10], 1):
            if result.get('success'):
                post = result['post']
                report.append(f"{i}. **@{post['username']}** - {post['outlier_factor']:.1f}x | {post['likes']:,} likes")
                report.append(f"   {post.get('caption', '')[:100]}...")
                report.append("")
        
        return "\n".join(report)
    
    def push_to_github(self):
        """Push updates to GitHub repository"""
        print("\n📤 Pushing to GitHub...")
        
        try:
            # Git commands
            subprocess.run(["git", "add", "data/"], cwd=self.workspace, check=True)
            
            commit_msg = f"ContentRadar scan: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.workspace, check=True)
            
            subprocess.run(["git", "push"], cwd=self.workspace, check=True)
            
            print("  ✅ Pushed to GitHub")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Git push failed: {e}")
    
    def send_telegram_alert(self, major_outliers: List[Dict]):
        """Send Telegram alert for major outliers (>10x)"""
        if not major_outliers:
            return
        
        print(f"\n📲 Sending Telegram alert for {len(major_outliers)} major outliers...")
        
        # Use OpenClaw message tool (via subprocess call to parent agent)
        # For now, just print the alert text
        alert_lines = ["🚨 *ContentRadar Major Outlier Alert!*\n"]
        
        for outlier in major_outliers:
            post = outlier['post']
            alert_lines.append(f"📈 *@{post['username']}* - {post['outlier_factor']:.1f}x average")
            alert_lines.append(f"   💙 {post['likes']:,} likes | 💬 {post['comments']:,} comments")
            alert_lines.append(f"   🔗 {post['url']}\n")
        
        alert_text = "\n".join(alert_lines)
        
        # Write alert to file for parent agent to send
        alert_file = self.data_dir / "telegram_alert.txt"
        with open(alert_file, 'w') as f:
            f.write(alert_text)
        
        print(f"  ✅ Alert saved to {alert_file}")
        print("  ℹ️  Note: Parent agent should send via Telegram to thread 86 (ContentRadar)")
    
    def run(self):
        """Execute the full daily scan pipeline"""
        print("\n" + "="*60)
        print("🎯 CONTENTRADAR DAILY SCAN")
        print("="*60 + "\n")
        
        all_results = []
        
        # Process each creator
        for creator in self.config['creators']:
            username = creator['username']
            
            # 1. Scrape posts
            posts = self.scrape_posts(username, limit=self.config['scraping']['posts_per_creator'])
            
            if not posts:
                print(f"⚠️  No posts found for @{username}, skipping\n")
                continue
            
            # 2. Detect outliers
            outliers = self.detect_outliers(posts)
            
            if not outliers:
                print(f"ℹ️  No outliers found for @{username}\n")
                continue
            
            # 3. Process each outlier
            for i, outlier in enumerate(outliers):
                result = self.process_outlier(outlier, i)
                all_results.append(result)
        
        # 4. Generate summary report
        print("\n" + "="*60)
        print("📝 GENERATING SUMMARY REPORT")
        print("="*60)
        
        report = self.generate_summary_report(all_results)
        report_file = self.reports_dir / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"✅ Report saved: {report_file}")
        
        # 5. Push to GitHub
        self.push_to_github()
        
        # 6. Send Telegram alerts for major outliers
        major_outliers = [r for r in all_results if r.get('post', {}).get('is_major_outlier')]
        self.send_telegram_alert(major_outliers)
        
        print("\n" + "="*60)
        print("✅ CONTENTRADAR SCAN COMPLETE")
        print("="*60)
        print(f"📊 Total outliers processed: {len(all_results)}")
        print(f"🚨 Major outliers: {len(major_outliers)}")
        print(f"💾 Swipe files: {len([r for r in all_results if r.get('swipe_file')])}")
        print("")


def main():
    """Main entry point"""
    try:
        radar = ContentRadar()
        radar.run()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
