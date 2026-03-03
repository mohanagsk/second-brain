# ContentRadar 🎯

Automated Instagram content intelligence system. Scrapes watchlist creators, detects viral outliers, and generates actionable swipe files with AI analysis.

## Features

- 📊 **Scrape** last 100 posts per creator (Apify Instagram scraper)
- 🎯 **Detect** outliers (>3x average engagement)
- 📹 **Download** outlier videos (yt-dlp)
- 🎵 **Extract** audio (ffmpeg) + first 5 frames
- 🎙️ **Transcribe** with Groq Whisper (romanized English)
- 🧠 **Analyze** content with Claude Sonnet 4.5
- 🎨 **Analyze** visuals with Gemini 2.0 Flash
- 📝 **Generate** detailed swipe file entries
- 🚀 **Push** to GitHub automatically
- 📲 **Alert** via Telegram for major outliers (>10x)

## Setup

### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg yt-dlp

# macOS
brew install ffmpeg yt-dlp
```

### 2. Install Python Dependencies
```bash
cd instagram-intel
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Required
export ANTHROPIC_API_KEY="your_claude_key"
export GROQ_API_KEY="your_groq_key"

# Already in workspace/credentials/:
# - apify-creds.env (APIFY_TOKEN)
# - gemini-key.env (GEMINI_API_KEY)
```

### 4. Edit Watchlist
Edit `config/watchlist.yaml` to add/remove creators:
```yaml
creators:
  - username: creator1
    platform: instagram
  - username: creator2
    platform: instagram
```

## Usage

### Run Daily Scan
```bash
cd instagram-intel/src
python daily_scan.py
```

### Test Individual Components

**Test media processing:**
```bash
python -c "from media import MediaProcessor; mp = MediaProcessor(); print('✅ Media processor ready')"
```

**Test transcription:**
```bash
python transcribe.py path/to/audio.mp3
```

**Test analysis:**
```bash
python -c "from analyze import ContentAnalyzer; ca = ContentAnalyzer(); print('✅ Analyzer ready')"
```

## Output Structure

```
instagram-intel/
├── config/
│   └── watchlist.yaml          # Creator watchlist
├── src/
│   ├── daily_scan.py           # Main orchestrator
│   ├── media.py                # FFmpeg wrapper
│   ├── transcribe.py           # Groq Whisper
│   └── analyze.py              # Claude + Gemini
├── data/
│   ├── downloads/              # Downloaded videos
│   ├── processed/              # Extracted audio/frames
│   ├── swipe_files/            # Generated swipe file entries
│   └── reports/                # Daily scan reports
└── requirements.txt
```

## Swipe File Format

Each outlier generates a markdown file with:
- Post metadata (likes, comments, views, engagement rate)
- Caption
- Full transcription
- Claude content analysis (hook, structure, engagement drivers, tactics)
- Gemini visual analysis (style, composition, editing, techniques)
- Quick takeaways

## Automation

### Schedule Daily Scans
```bash
# Add to crontab (run at 9 AM daily)
0 9 * * * cd /home/divykairoth/.openclaw/workspace/instagram-intel/src && /usr/bin/python3 daily_scan.py >> /var/log/contentradar.log 2>&1
```

### Telegram Alerts
Major outliers (>10x average) generate an alert file:
`data/telegram_alert.txt`

Parent OpenClaw agent can send via:
```bash
# Send to ContentRadar thread (86)
cat data/telegram_alert.txt | openclaw message send --target=-1003763057831 --thread=86
```

## Workflow

1. **Scrape** → Apify fetches last 100 posts per creator
2. **Detect** → Calculate avg engagement, flag >3x outliers
3. **Download** → yt-dlp pulls video files
4. **Extract** → ffmpeg splits audio + 5 evenly-spaced frames
5. **Transcribe** → Groq Whisper converts audio to text
6. **Analyze Content** → Claude analyzes hook, structure, engagement
7. **Analyze Visuals** → Gemini analyzes style, composition, techniques
8. **Generate Swipe** → Formatted markdown with all insights
9. **Report** → Summary of scan results
10. **Push** → Git commit + push to GitHub
11. **Alert** → Telegram notification for >10x outliers

## Credentials Required

| Service | Key | Location |
|---------|-----|----------|
| Apify | `APIFY_TOKEN` | `~/.openclaw/workspace/credentials/apify-creds.env` |
| Groq | `GROQ_API_KEY` | Environment variable |
| Claude | `ANTHROPIC_API_KEY` | Environment variable |
| Gemini | `GEMINI_API_KEY` | `~/.openclaw/workspace/credentials/gemini-key.env` |

## Troubleshooting

**Apify scraping fails:**
- Check token validity
- Verify username format (no @ symbol in API call)
- Instagram may rate limit - wait 1 hour

**Video download fails:**
- Ensure yt-dlp is up to date: `yt-dlp -U`
- Some videos may be private/geo-blocked

**Transcription fails:**
- Check GROQ_API_KEY is set
- Verify audio file is valid (not corrupted)

**Analysis fails:**
- Check API keys are valid
- Claude/Gemini may have rate limits
- Network issues - retry after delay

## Future Enhancements

- [ ] Support for TikTok, YouTube Shorts
- [ ] Historical trend analysis
- [ ] Competitor comparison reports
- [ ] Auto-posting of top swipe files to Notion
- [ ] Video similarity clustering
- [ ] Hook pattern extraction and taxonomy

## License

Private - Divy's internal tool

---

Built with ❤️ by Mohana (AI Agent) for Divy
