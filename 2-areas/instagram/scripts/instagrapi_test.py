#!/usr/bin/env python3
"""Test instagrapi login and basic scraping"""
import json
import os
from pathlib import Path

# Add venv to path
import sys
sys.path.insert(0, '/home/divykairoth/.openclaw/workspace/instagrapi-venv/lib/python3.11/site-packages')

from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, 
    ChallengeRequired, 
    TwoFactorRequired,
    PleaseWaitFewMinutes,
    RateLimitError
)

USERNAME = "divy.kairoth"
PASSWORD = os.environ.get("IG_PASSWORD", "")
SESSION_FILE = Path("/home/divykairoth/.openclaw/workspace/credentials/instagram_session.json")

def test_login():
    cl = Client()
    
    # Set device/user agent to look more realistic
    cl.set_user_agent("Instagram 269.0.0.18.75 Android (31/12; 420dpi; 1080x2340; Google/google; Pixel 5; redfin; redfin; en_US; 436384447)")
    
    # Try to load existing session first
    if SESSION_FILE.exists():
        print("📂 Found existing session, loading...")
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            print("✅ Logged in using saved session!")
        except Exception as e:
            print(f"⚠️ Session expired: {e}")
            SESSION_FILE.unlink()
    
    if not cl.user_id:
        print("🔐 Attempting fresh login...")
        try:
            cl.login(USERNAME, PASSWORD)
            print("✅ Fresh login successful!")
            # Save session for future use
            cl.dump_settings(SESSION_FILE)
            print(f"💾 Session saved to {SESSION_FILE}")
        except TwoFactorRequired:
            print("🔑 2FA required - need verification code")
            return None
        except ChallengeRequired as e:
            print(f"🚫 Challenge required: {e}")
            print("   Instagram wants to verify you're human")
            print("   Option 1: Log in via browser and export cookies")
            print("   Option 2: Use Playwright to handle challenge")
            return None
        except PleaseWaitFewMinutes as e:
            print(f"⏰ Rate limited: {e}")
            return None
        except RateLimitError as e:
            print(f"🚫 Rate limit: {e}")
            return None
        except Exception as e:
            print(f"❌ Login failed: {type(e).__name__}: {e}")
            return None
    
    return cl

def test_scrape(cl):
    """Test basic scraping after login"""
    print("\n📊 Testing scrape capabilities...")
    
    try:
        # Get own profile info
        user = cl.user_info_by_username(USERNAME)
        print(f"✅ Profile: {user.username} | {user.follower_count} followers | {user.media_count} posts")
        
        # Get recent reels
        print("\n🎬 Fetching recent reels...")
        user_id = cl.user_id_from_username(USERNAME)
        reels = cl.user_clips(user_id, amount=5)
        
        print(f"✅ Got {len(reels)} reels:")
        for i, reel in enumerate(reels[:5], 1):
            views = getattr(reel, 'play_count', 0) or getattr(reel, 'view_count', 0) or 0
            likes = getattr(reel, 'like_count', 0)
            print(f"   {i}. {reel.pk} | {views:,} views | {likes:,} likes")
        
        return True
        
    except Exception as e:
        print(f"❌ Scrape failed: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("INSTAGRAPI LOGIN TEST")
    print("=" * 50)
    
    cl = test_login()
    if cl:
        test_scrape(cl)
    else:
        print("\n⚠️ Login failed - try Playwright browser approach")
