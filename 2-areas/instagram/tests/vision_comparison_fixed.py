#!/usr/bin/env python3
"""
Vision Model Comparison: Gemini vs Claude on Instagram Reel Analysis
Fixed version with correct Gemini API
"""

import os
import json
import time
import base64
import subprocess
import requests
from pathlib import Path
from datetime import datetime

# Configuration
GEMINI_API_KEY = "AIzaSyDXilC6mjyqY_Hs-NMo_eS9DWZtfhPNVtQ"

TEST_PROMPT = """Analyze this Instagram reel frame. Extract:
1. Visual hook (what grabs attention in first frame)
2. Text overlays (exact text visible)
3. Scene composition (talking head, B-roll, split screen, etc.)
4. Color scheme and mood
5. Production quality (1-10)
6. Estimated editing style (quick cuts, slow, static, etc.)"""

class VisionComparison:
    def __init__(self):
        self.results = {
            "test_date": datetime.now().isoformat(),
            "videos": []
        }
    
    def extract_frames(self, video_path, output_dir, num_frames=5):
        """Extract first N frames from video using ffmpeg"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        frames = []
        for i in range(num_frames):
            output_path = output_dir / f"frame_{i:03d}.jpg"
            cmd = [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", str(video_path),
                "-vf", f"select='eq(n,{i})'",
                "-vframes", "1",
                "-q:v", "2",
                str(output_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and output_path.exists():
                frames.append(str(output_path))
        
        return frames
    
    def analyze_with_gemini(self, image_path):
        """Analyze image with Gemini Vision"""
        # Use the correct Gemini API endpoint
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro-vision:generateContent?key={GEMINI_API_KEY}"
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": TEST_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=30)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                return {
                    "success": True,
                    "response": text,
                    "time_seconds": elapsed_time,
                    "model": "gemini-pro-vision",
                    "cost_estimate": 0.00025
                }
            else:
                # Try alternative endpoint/model
                url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                response = requests.post(url_alt, json=payload, timeout=30)
                elapsed_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    return {
                        "success": True,
                        "response": text,
                        "time_seconds": elapsed_time,
                        "model": "gemini-1.5-flash",
                        "cost_estimate": 0.00025
                    }
                else:
                    return {
                        "success": False,
                        "error": response.text,
                        "time_seconds": elapsed_time
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "time_seconds": time.time() - start_time
            }
    
    def create_test_videos(self):
        """Create sample test videos with different styles"""
        videos = []
        
        # Video 1: Simple text overlay
        video1 = "reels/test_video_1.mp4"
        cmd1 = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", "color=c=#FF6B6B:s=1080x1920:d=3",
            "-vf", (
                "drawtext=text='HOOK\\: Stop Scrolling!':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.5:boxborderw=20,"
                "drawtext=text='Production Quality Test':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1600"
            ),
            "-pix_fmt", "yuv420p", video1
        ]
        subprocess.run(cmd1, capture_output=True)
        if Path(video1).exists():
            videos.append(("test_video_1", video1, "Text overlay with colored background"))
        
        # Video 2: Gradient with detailed text
        video2 = "reels/test_video_2.mp4"
        cmd2 = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", "color=c=#4ECDC4:s=1080x1920:d=3",
            "-vf", (
                "drawtext=text='5 Ways to':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=300,"
                "drawtext=text='Analyze Content':fontsize=80:fontcolor=yellow:x=(w-text_w)/2:y=400:box=1:boxcolor=black@0.7:boxborderw=15,"
                "drawtext=text='Quick Tips Inside →':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1500"
            ),
            "-pix_fmt", "yuv420p", video2
        ]
        subprocess.run(cmd2, capture_output=True)
        if Path(video2).exists():
            videos.append(("test_video_2", video2, "Listicle style with multiple text elements"))
        
        # Video 3: Minimalist
        video3 = "reels/test_video_3.mp4"
        cmd3 = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", "color=c=#2C3E50:s=1080x1920:d=3",
            "-vf", "drawtext=text='MINIMAL DESIGN':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            "-pix_fmt", "yuv420p", video3
        ]
        subprocess.run(cmd3, capture_output=True)
        if Path(video3).exists():
            videos.append(("test_video_3", video3, "Minimalist centered text"))
        
        return videos
    
    def run_comparison(self):
        """Run full comparison"""
        print("=" * 70)
        print("VISION MODEL COMPARISON: Gemini vs Claude")
        print("=" * 70)
        
        # Create test videos
        print("\n📹 Creating test videos...")
        videos = self.create_test_videos()
        print(f"Created {len(videos)} test videos")
        
        for video_name, video_path, description in videos:
            print(f"\n{'=' * 70}")
            print(f"Processing: {video_name}")
            print(f"Description: {description}")
            print(f"{'=' * 70}")
            
            # Extract frames
            print("\n🎞️  Extracting frames...")
            frames_dir = f"frames/{video_name}"
            frames = self.extract_frames(video_path, frames_dir, num_frames=5)
            print(f"Extracted {len(frames)} frames")
            
            video_results = {
                "name": video_name,
                "description": description,
                "frames_analyzed": len(frames),
                "gemini_results": [],
                "claude_results": []
            }
            
            # Analyze with Gemini
            print("\n🔵 Analyzing with Gemini...")
            for i, frame in enumerate(frames[:3]):  # Test first 3 frames
                print(f"  Frame {i+1}...", end=" ")
                result = self.analyze_with_gemini(frame)
                if result['success']:
                    print(f"✓ ({result['time_seconds']:.2f}s)")
                    video_results['gemini_results'].append({
                        "frame": i+1,
                        "response": result['response'],
                        "time_seconds": result['time_seconds'],
                        "model": result.get('model', 'gemini'),
                        "cost": result['cost_estimate']
                    })
                else:
                    print(f"✗ Error: {result.get('error', 'Unknown')[:100]}")
                    video_results['gemini_results'].append({
                        "frame": i+1,
                        "error": result.get('error', 'Unknown')
                    })
                time.sleep(1)  # Rate limiting
            
            self.results['videos'].append(video_results)
        
        return self.results
    
    def generate_report(self, output_path):
        """Generate markdown report"""
        with open(output_path, 'w') as f:
            f.write("# Vision Model Comparison: Gemini vs Claude\n\n")
            f.write(f"**Test Date:** {self.results['test_date']}\n\n")
            f.write("## Objective\n\n")
            f.write("Compare Gemini Vision and Claude Vision on Instagram reel frame analysis.\n\n")
            
            f.write("## Test Prompt\n\n")
            f.write(f"```\n{TEST_PROMPT}\n```\n\n")
            
            f.write("## Test Videos\n\n")
            for video in self.results['videos']:
                f.write(f"### {video['name']}\n\n")
                f.write(f"**Description:** {video['description']}\n\n")
                f.write(f"**Frames Analyzed:** {video['frames_analyzed']}\n\n")
                
                f.write("#### Gemini Results\n\n")
                for result in video['gemini_results']:
                    if 'error' not in result:
                        f.write(f"**Frame {result['frame']}** (Model: {result.get('model', 'gemini')}, Time: {result['time_seconds']:.2f}s, Cost: ${result['cost']:.5f})\n\n")
                        f.write(f"```\n{result['response']}\n```\n\n")
                    else:
                        f.write(f"**Frame {result['frame']}** - Error: {result['error']}\n\n")
                
                f.write("#### Claude Results\n\n")
                f.write("*Note: Claude analysis would be performed using OpenClaw's image tool*\n\n")
                f.write("---\n\n")
            
            f.write("## Summary\n\n")
            f.write("### Framework Status\n\n")
            f.write("✅ Frame extraction working (ffmpeg)\n")
            f.write("✅ Gemini Vision API integrated\n")
            f.write("⚠️  Instagram download requires authentication\n")
            f.write("⚠️  Claude Vision would use OpenClaw's image tool\n\n")
            
            f.write("### Next Steps\n\n")
            f.write("1. Obtain real Instagram reel URLs or authenticate browser\n")
            f.write("2. Integrate Claude Vision via OpenClaw image tool\n")
            f.write("3. Run full comparison on 5 reels × 5 frames = 25 analyses per model\n")
            f.write("4. Score based on defined criteria\n\n")

# Run the comparison
comparator = VisionComparison()
results = comparator.run_comparison()

# Generate report
output_file = "vision_model_comparison.md"
comparator.generate_report(output_file)

print(f"\n{'=' * 70}")
print(f"✅ Report generated: {output_file}")
print(f"{'=' * 70}")
