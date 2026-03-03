#!/usr/bin/env python3
"""
Vision Model Comparison: Gemini vs Claude on Instagram Reel Analysis
"""

import os
import json
import time
import base64
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
GEMINI_API_KEY = "AIzaSyDXilC6mjyqY_Hs-NMo_eS9DWZtfhPNVtQ"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

TEST_PROMPT = """Analyze this Instagram reel frame. Extract:
1. Visual hook (what grabs attention in first frame)
2. Text overlays (exact text visible)
3. Scene composition (talking head, B-roll, split screen, etc.)
4. Color scheme and mood
5. Production quality (1-10)
6. Estimated editing style (quick cuts, slow, static, etc.)"""

def extract_frames(video_path, output_dir, num_frames=5):
    """Extract first N frames from video using ffmpeg"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    frames = []
    for i in range(num_frames):
        output_path = output_dir / f"frame_{i:03d}.jpg"
        cmd = [
            "ffmpeg", "-y",
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

def analyze_with_gemini(image_path):
    """Analyze image with Gemini Vision"""
    import requests
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # Prepare request
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
    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return {
            "success": True,
            "response": text,
            "time_seconds": elapsed_time,
            "cost_estimate": 0.00025  # Approximate cost per image
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "time_seconds": elapsed_time
        }

def analyze_with_claude(image_path):
    """Analyze image with Claude Vision (using OpenClaw's image tool would be used here)"""
    # Note: In actual implementation, this would use the OpenClaw image tool
    # For this demo, I'll return a placeholder
    return {
        "success": True,
        "response": "[Claude analysis would go here - using OpenClaw's image tool]",
        "time_seconds": 0,
        "cost_estimate": 0.003  # Approximate cost per image for Claude
    }

def create_sample_video():
    """Create a sample test video for demonstration"""
    output_path = "reels/sample_test.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=blue:s=1080x1920:d=5",
        "-vf", f"drawtext=text='TEST VIDEO FOR VISION MODEL COMPARISON':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path if Path(output_path).exists() else None

print("Vision Model Comparison Script")
print("=" * 60)
print("\nNote: Due to Instagram login requirements, using sample test data")
print("This demonstrates the comparison methodology\n")

# Create sample video
print("Creating sample test video...")
sample_video = create_sample_video()
if not sample_video:
    print("Error: Could not create sample video")
    exit(1)

print(f"Created: {sample_video}")

# Extract frames
print("\nExtracting frames...")
frames = extract_frames(sample_video, "frames/sample", num_frames=5)
print(f"Extracted {len(frames)} frames")

# Test Gemini on first frame
if frames:
    print("\n" + "=" * 60)
    print("Testing Gemini Vision API...")
    print("=" * 60)
    
    result = analyze_with_gemini(frames[0])
    if result['success']:
        print(f"\n✓ Success!")
        print(f"Response time: {result['time_seconds']:.2f}s")
        print(f"Estimated cost: ${result['cost_estimate']:.5f}")
        print(f"\nGemini Response:\n{result['response'][:500]}...")
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 60)
print("Comparison Framework Ready")
print("=" * 60)
print("\nTo complete the comparison with real Instagram reels:")
print("1. Provide direct reel URLs or downloaded videos")
print("2. Run frame extraction on each")
print("3. Analyze with both models")
print("4. Score and compare results")
