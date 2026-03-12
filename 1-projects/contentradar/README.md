# 📡 ContentRadar

DIY viral content intelligence tool. Find outlier videos across YouTube, Instagram, and TikTok — the ones that massively outperformed a channel's average.

**Why?** Sandcastles.ai charges $39-499/mo for this. ContentRadar does it for free.

## Quick Start

```bash
# Scan a YouTube channel for outlier videos
python3 -m contentradar scan youtube -c @mkbhd

# Multiple channels at once
python3 -m contentradar scan youtube -c @mkbhd -c @MrBeast -c @divykairoth

# Lower threshold to catch more
python3 -m contentradar scan youtube -c @mkbhd -t 2.0

# Quick mode (terminal only, no files saved)
python3 -m contentradar scan youtube -c @mkbhd -q

# Export as CSV
python3 -m contentradar scan youtube -c @mkbhd --output csv

# Export as JSON
python3 -m contentradar scan youtube -c @mkbhd --output json
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-c, --channel` | required | YouTube handle, URL, or channel ID (repeatable) |
| `-l, --limit` | 50 | Max videos to fetch per channel |
| `-t, --threshold` | 3.0 | Min outlier score (views / channel avg) |
| `-m, --method` | mean | Avg calculation: `mean` or `median` |
| `-w, --window` | all | Time window: `30d`, `90d`, `365d`, `all` |
| `-o, --output` | table | Output format: `table`, `json`, `csv` |
| `-q, --quick` | false | Terminal only, skip file saves |
| `--no-save` | false | Don't save raw data or outlier files |

## How It Works

1. Fetches recent videos from a channel using `yt-dlp`
2. Calculates the channel's average view count
3. Scores each video: `outlier_score = views / channel_average`
4. Flags videos above the threshold (default 3x average)
5. Saves raw data + outliers to `data/` directory

## Output Files

```
data/
├── raw/youtube/@channel.json       # All fetched videos
└── outliers/youtube/
    ├── @channel.json               # Outlier analysis
    └── @channel.csv                # CSV export
```

## Architecture

```
contentradar/
├── __main__.py          # Entry point
├── cli.py               # Click CLI
├── core/
│   ├── youtube.py       # yt-dlp video fetcher
│   └── outlier.py       # Outlier detection engine
├── output/
│   ├── terminal.py      # Rich terminal output
│   └── csv_writer.py    # CSV export
├── config/              # Settings
├── data/                # Output files
└── requirements.txt
```

## Requirements

- Python 3.11+
- yt-dlp (installed)
- Dependencies: `pip install click rich`

## Roadmap

- [x] Phase 1: YouTube outlier detection
- [ ] Phase 2: Instagram outlier detection (via Apify)
- [ ] Phase 3: AI analysis pipeline (Groq transcription + Claude analysis)
- [ ] Phase 4: TikTok support
- [ ] Phase 5: Watchlist & scheduling
- [ ] Phase 6: Script generator
- [ ] Phase 7: Web dashboard

## Credits

Inspired by [Sandcastles.ai](https://sandcastles.ai). Built by Mohana for Divy.
