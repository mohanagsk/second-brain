# REQUIREMENTS.md — ContentRadar Instagram Intel

---

## Functional Requirements

### FR1: Instagram Scraping
- **FR1.1:** Scrape last 100 posts from any public Instagram creator
- **FR1.2:** Extract: views, likes, comments, engagement rate, caption, hashtags, timestamp, video URL, audio info
- **FR1.3:** Handle rate limits gracefully (Apify manages this)
- **FR1.4:** Support multiple creators in single run

### FR2: Outlier Detection  
- **FR2.1:** Calculate channel average from 100 most recent posts
- **FR2.2:** Score each post: `outlier_score = views / avg_views`
- **FR2.3:** Flag posts with score >3.0 as outliers
- **FR2.4:** Flag posts with score >10.0 as major outliers
- **FR2.5:** Filter out collaborations (optional flag)
- **FR2.6:** Detect duplicate reels (same content, different URLs)

### FR3: Media Processing
- **FR3.1:** Download video files via yt-dlp
- **FR3.2:** Extract audio track as MP3 via ffmpeg
- **FR3.3:** Extract first 5 frames as JPG via ffmpeg
- **FR3.4:** Delete media after analysis (configurable)

### FR4: Transcription
- **FR4.1:** Transcribe audio using Groq Whisper
- **FR4.2:** Output in romanized format (lang=en parameter)
- **FR4.3:** Handle Hindi, English, Hinglish content
- **FR4.4:** Include timestamps (optional)

### FR5: Vision Analysis
- **FR5.1:** Analyze first frame for visual hook
- **FR5.2:** Extract text overlays (OCR)
- **FR5.3:** Identify scene composition (talking head, B-roll, etc.)
- **FR5.4:** Assess thumbnail quality (1-10)

### FR6: Content Analysis
- **FR6.1:** Score hook effectiveness (1-10)
- **FR6.2:** Detect curiosity loops (7 types)
- **FR6.3:** Analyze CTA placement and effectiveness
- **FR6.4:** Identify emotional triggers
- **FR6.5:** Generate replication template
- **FR6.6:** Predict viral potential

### FR7: Swipe Files
- **FR7.1:** Auto-append new patterns to swipe files
- **FR7.2:** Maintain table format with scores
- **FR7.3:** Categories: hooks, visual hooks, CTAs, curiosity loops, audio
- **FR7.4:** Include example reel URLs
- **FR7.5:** Track which patterns are proven (confidence score)

### FR8: Hypothesis System
- **FR8.1:** Generate hypotheses from detected patterns
- **FR8.2:** Track hypothesis test results
- **FR8.3:** Update confidence weights based on outcomes
- **FR8.4:** Weekly hypothesis performance report

### FR9: Trending Audio
- **FR9.1:** Track audio usage across scraped reels
- **FR9.2:** Identify audio appearing in multiple outliers
- **FR9.3:** Classify trend status: rising, peaking, falling
- **FR9.4:** Recommend audio for content type

### FR10: Daily Automation
- **FR10.1:** Run automatically at 10 AM IST via cron
- **FR10.2:** Load creators from watchlist config
- **FR10.3:** Process new posts since last run
- **FR10.4:** Push results to GitHub
- **FR10.5:** Send Telegram alert for major outliers

---

## Non-Functional Requirements

### NFR1: Performance
- Scrape 100 posts per creator in <30 seconds
- Analyze single reel in <60 seconds
- Complete daily scan of 5 creators in <10 minutes

### NFR2: Cost
- Monthly cost <$10 for typical usage (500 reels)
- Use free tiers where available (Groq, Gemini)
- No GPT-4 API (removed per Divy's request)

### NFR3: Reliability
- Handle API failures gracefully with retries
- Log all errors for debugging
- Skip failed reels, continue with others

### NFR4: Storage
- All analysis stored in GitHub (second-brain repo)
- Local storage for temporary video files only
- Clean up temp files after processing

### NFR5: Maintainability
- Modular Python scripts
- Configuration via YAML files
- Clear logging output

---

## Constraints

### C1: API Limitations
- Apify: Pay per result ($0.50/1K)
- Instagram: No direct API access for views
- Groq: Rate limits on free tier

### C2: Authentication
- Instagram scraping blocked from datacenter IPs
- Using Apify solves this (their proxies)
- No Instagram login required

### C3: Models
- Claude Sonnet/Opus only (no GPT-4)
- Gemini for vision (free via GCP)
- Groq Whisper for transcription

### C4: Platforms
- Instagram Reels ONLY for v1
- No TikTok, YouTube, Stories

---

## Acceptance Criteria

### AC1: Scraping Works
```bash
python scan @divy.kairoth
# Returns: JSON with 100 posts, all fields populated
# Views field must have actual numbers (not null)
```

### AC2: Outliers Detected
```bash
python scan @divy.kairoth --outliers
# Returns: Only posts with score >3.0
# Includes outlier_score field
```

### AC3: Analysis Complete
```bash
python analyze reel_id
# Returns: Full analysis with hook score, loops, CTAs
# Saves to swipe file automatically
```

### AC4: Daily Automation
```bash
python daily_scan
# Processes all watchlist creators
# Pushes to GitHub
# Sends Telegram alert if major outlier found
```
