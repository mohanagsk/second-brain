# ContentRadar Quick Start

## 1. Install Dependencies (one-time)

```bash
cd instagram-intel
./install.sh
```

Or manually:
```bash
pip install -r requirements.txt
```

## 2. Set Environment Variables

```bash
# Add to ~/.bashrc or export in current shell
export ANTHROPIC_API_KEY="your_claude_api_key"
export GROQ_API_KEY="your_groq_api_key"
```

Other credentials are already configured in `~/.openclaw/workspace/credentials/`:
- ✅ `apify-creds.env` (Apify)
- ✅ `gemini-key.env` (Gemini)

## 3. Customize Watchlist (optional)

Edit `config/watchlist.yaml`:
```yaml
creators:
  - username: divy.kairoth
    platform: instagram
  - username: your_creator_here
    platform: instagram
```

## 4. Run Daily Scan

```bash
cd instagram-intel/src
python daily_scan.py
```

## What It Does

1. **Scrapes** last 100 posts per creator (Apify)
2. **Detects** outliers (>3x average engagement)
3. **Downloads** outlier videos (yt-dlp)
4. **Extracts** audio + 5 frames (ffmpeg)
5. **Transcribes** audio (Groq Whisper)
6. **Analyzes** content (Claude) + visuals (Gemini)
7. **Generates** swipe file entries
8. **Commits** to GitHub
9. **Alerts** via Telegram for major outliers (>10x)

## Output

```
data/
├── downloads/           # Downloaded videos
├── processed/          # Audio files + frames
├── swipe_files/        # Analysis markdown files
└── reports/            # Daily scan summaries
```

## Validate Setup

```bash
python test_setup.py
```

Should show all ✅ checks passing.

## Telegram Alerts

Major outliers (>10x avg) generate `data/telegram_alert.txt`.

Parent agent sends to ContentRadar topic (thread 86):
```bash
cat data/telegram_alert.txt | openclaw message send --target=-1003763057831 --thread=86
```

## Automate (Cron)

```bash
# Add to crontab: run daily at 9 AM IST
crontab -e

# Add this line:
0 9 * * * cd /home/divykairoth/.openclaw/workspace/instagram-intel/src && /usr/bin/python3 daily_scan.py >> /var/log/contentradar.log 2>&1
```

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**"yt-dlp not found"**
```bash
sudo apt-get install yt-dlp
# or: pip install yt-dlp
```

**"Apify scraping failed"**
- Check token in `~/.openclaw/workspace/credentials/apify-creds.env`
- Verify username format (no @ symbol)
- Wait 1 hour if rate limited

**"Transcription failed"**
```bash
export GROQ_API_KEY="gsk_..."
```

## Example Run Output

```
============================================================
🎯 CONTENTRADAR DAILY SCAN
============================================================

🔍 Scraping @divy.kairoth (last 100 posts)...
  ⏳ Run started: abc123
  ✅ Scraping completed
  📊 Found 97 posts

🎯 Found 3 outliers (avg engagement: 2,450)
  📈 5.2x - 12,740 likes
  📈 3.8x - 9,310 likes
  📈 3.1x - 7,590 likes

============================================================
Processing outlier #1: @divy.kairoth
Factor: 5.2x | Likes: 12,740
============================================================
  ✅ Downloaded: divy.kairoth_1.mp4
  🎵 Extracting audio...
  🎬 Extracting frames...
  ✅ Extracted 5 frames
  🎙️  Transcribing audio...
  ✅ Transcribed (34.2s)
  🧠 Analyzing content (Claude)...
  🎨 Analyzing visuals (Gemini)...
  📝 Generating swipe file...
  ✅ Saved: 20250303_divy.kairoth_1.md

...

============================================================
✅ CONTENTRADAR SCAN COMPLETE
============================================================
📊 Total outliers processed: 3
🚨 Major outliers: 0
💾 Swipe files: 3
```

## Next Steps

1. Review generated swipe files in `data/swipe_files/`
2. Check daily report in `data/reports/`
3. Set up cron for daily automation
4. Integrate Telegram alerts with main agent

---

**Need help?** Check `README.md` for detailed documentation.
