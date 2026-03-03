#!/usr/bin/env python3
"""Login to Instagram via Playwright and export session"""
import asyncio
import json
import os
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...")
    os.system("pip install playwright --quiet")
    os.system("playwright install chromium")
    from playwright.async_api import async_playwright

USERNAME = "divy.kairoth"
PASSWORD = os.environ.get("IG_PASSWORD", "")
COOKIES_FILE = Path("/home/divykairoth/.openclaw/workspace/credentials/instagram_cookies.json")

async def login_instagram():
    async with async_playwright() as p:
        # Use persistent context to save session
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("🌐 Navigating to Instagram...")
        await page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Check if already blocked
        content = await page.content()
        if "suspicious" in content.lower() or "unusual" in content.lower():
            print("🚫 Instagram blocked this IP (suspicious activity)")
            await browser.close()
            return False
        
        # Accept cookies if dialog appears
        try:
            await page.click("text=Allow all cookies", timeout=3000)
        except:
            pass
        
        print("📝 Entering credentials...")
        await page.fill('input[name="username"]', USERNAME)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        
        print("⏳ Waiting for login result...")
        await asyncio.sleep(5)
        
        # Check for various outcomes
        url = page.url
        content = await page.content()
        
        if "challenge" in url:
            print("🔐 Challenge required - Instagram wants verification")
            print("   You need to verify from a trusted device")
            await browser.close()
            return False
        
        if "two_factor" in url:
            print("🔑 2FA required")
            await browser.close()
            return False
            
        if "onetap" in url or "/accounts/onetap" in url:
            print("✅ Login successful! (save login prompt)")
            
        if USERNAME in content or "logged-in" in content or "Feed" in content:
            print("✅ Login successful!")
            
            # Export cookies
            cookies = await context.cookies()
            COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
            print(f"🍪 Saved {len(cookies)} cookies to {COOKIES_FILE}")
            
            await browser.close()
            return True
        
        print(f"⚠️ Unknown state. URL: {url}")
        print(f"   Saving screenshot for debug...")
        await page.screenshot(path="/tmp/ig_login_debug.png")
        
        await browser.close()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PLAYWRIGHT INSTAGRAM LOGIN")
    print("=" * 50)
    result = asyncio.run(login_instagram())
    if not result:
        print("\n💡 Alternative: Use Browser Relay")
        print("   1. Open Instagram in Chrome")
        print("   2. Log in manually")
        print("   3. Click OpenClaw extension icon")
        print("   4. I'll export the cookies from there")
