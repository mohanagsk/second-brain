# ContentRadar v2 — Product Requirements Document

**Version:** 2.0  
**Date:** March 3, 2026  
**Author:** Mohana  
**Method:** GSD (Get Shit Done) spec-driven development

---

## Executive Summary

ContentRadar v2 extends the existing YouTube outlier detection tool to become a **complete viral content intelligence system** covering Instagram, TikTok, and YouTube — with AI-powered analysis, swipe file generation, and hypothesis testing.

**Target:** Replace Sandcastles.ai ($39-499/mo) and Blort AI ($39-59/mo) with a free/cheap self-hosted alternative.

---

## Competitor Analysis Summary

| Tool | Price | Strengths | Gaps |
|------|-------|-----------|------|
| **Sandcastles.ai** | $39-499/mo | Script gen, hook templates, 50 creator tracking | No Hindi, expensive API |
| **Blort AI** | $39-59/mo | Frame-by-frame analysis, multi-model, API | New, less mature |
| **ContentRadar v1** | FREE | YouTube outliers working | No Instagram, no AI analysis |

**Our Moat:** Free, self-hosted, Hindi support, full control, open source potential.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTENTRADAR V2 ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                    │
│  │   INPUT     │     │  SCRAPING   │     │  DOWNLOAD   │                    │
│  │             │     │             │     │             │                    │
│  │ - Username  │────▶│ - Apify     │────▶│ - yt-dlp    │                    │
│  │ - Platform  │     │ ($0.50/1K)  │     │ (FREE)      │                    │
│  │ - Timeframe │     │             │     │             │                    │
│  └─────────────┘     └─────────────┘     └─────────────┘                    │
│                              │                   │                           │
│                              ▼                   ▼                           │
│                      ┌─────────────┐     ┌─────────────┐                    │
│                      │  OUTLIER    │     │  MEDIA      │                    │
│                      │  DETECTION  │     │  PROCESSING │                    │
│                      │             │     │             │                    │
│                      │ - Score     │     │ - ffmpeg    │                    │
│                      │ - Collab    │     │   (frames)  │                    │
│                      │   filter    │     │ - Audio     │                    │
│                      │ - Promo     │     │   extract   │                    │
│                      │   filter    │     │             │                    │
│                      └─────────────┘     └─────────────┘                    │
│                              │                   │                           │
│                              ▼                   ▼                           │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                        AI ANALYSIS LAYER                          │      │
│  ├───────────────────────────────────────────────────────────────────┤      │
│  │                                                                    │      │
│  │   ┌────────────┐    ┌────────────┐    ┌────────────┐             │      │
│  │   │TRANSCRIBE  │    │  VISION    │    │  CONTENT   │             │      │
│  │   │            │    │  ANALYSIS  │    │  ANALYSIS  │             │      │
│  │   │ Groq       │    │            │    │            │             │      │
│  │   │ Whisper    │    │ Gemini     │    │ Claude     │             │      │
│  │   │ lang=en    │    │ 1.5 Pro    │    │ Sonnet     │             │      │
│  │   │ (romanize) │    │ (FREE)     │    │ ($0.01/ea) │             │      │
│  │   │            │    │            │    │            │             │      │
│  │   └────────────┘    └────────────┘    └────────────┘             │      │
│  │         │                 │                 │                     │      │
│  │         └─────────────────┼─────────────────┘                     │      │
│  │                           ▼                                       │      │
│  │                   ┌────────────┐                                  │      │
│  │                   │ SYNTHESIS  │                                  │      │
│  │                   │ (Optional) │                                  │      │
│  │                   │ Claude Opus│                                  │      │
│  │                   └────────────┘                                  │      │
│  │                           │                                       │      │
│  └───────────────────────────┼───────────────────────────────────────┘      │
│                              ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                        OUTPUT LAYER                               │      │
│  ├───────────────────────────────────────────────────────────────────┤      │
│  │                                                                    │      │
│  │   ┌────────────┐    ┌────────────┐    ┌────────────┐             │      │
│  │   │ SWIPE FILE │    │ HYPOTHESIS │    │  ALERTS    │             │      │
│  │   │            │    │            │    │            │             │      │
│  │   │ - Hooks    │    │ - Generate │    │ - Telegram │             │      │
│  │   │ - CTAs     │    │ - Track    │    │ - Daily    │             │      │
│  │   │ - Tactics  │    │ - Measure  │    │   digest   │             │      │
│  │   │ - Music    │    │            │    │            │             │      │
│  │   └────────────┘    └────────────┘    └────────────┘             │      │
│  │         │                 │                 │                     │      │
│  │         └─────────────────┼─────────────────┘                     │      │
│  │                           ▼                                       │      │
│  │                   ┌────────────┐                                  │      │
│  │                   │  GITHUB    │                                  │      │
│  │                   │  STORAGE   │                                  │      │
│  │                   │            │                                  │      │
│  │                   │ second-    │                                  │      │
│  │                   │ brain repo │                                  │      │
│  │                   └────────────┘                                  │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Decisions (Based on Tests)

| Component | Winner | Score | Cost | Rationale |
|-----------|--------|-------|------|-----------|
| **Scraping** | Apify (apidojo) | 88/100 | $0.50/1K | Only tool with views, reliable |
| **Download** | yt-dlp | 100/100 | FREE | Perfect success rate |
| **Transcription** | Groq Whisper | 78/100 | FREE | `lang=en` = romanized Hindi |
| **Vision** | Gemini 1.5 Pro | 85/100 | FREE | GCP credits, good quality |
| **Analysis** | Claude Sonnet | 90/100 | $0.01/ea | Best efficiency |
| **Synthesis** | Claude Opus | 95/100 | $0.07/ea | Monthly deep dives only |

---

## Phase Breakdown (GSD Style)

### Phase 1: Instagram Scraping Module ✅ READY
**Goal:** Add Instagram support to ContentRadar CLI

**Files to create:**
```
contentradar/
├── core/
│   ├── instagram.py      # NEW: Apify integration
│   └── outlier.py        # UPDATE: Add platform param
├── cli.py                # UPDATE: Add instagram command
```

**Commands:**
```bash
python3 -m contentradar scan instagram -u @divy.kairoth
python3 -m contentradar scan instagram -u @divy.kairoth -u @jaykapoor.24
```

**Acceptance criteria:**
- [ ] Scrapes reels via Apify API
- [ ] Returns views, likes, comments, engagement rate
- [ ] Calculates outlier scores
- [ ] Filters collaborations (optional flag)
- [ ] Outputs JSON/CSV/table

---

### Phase 2: Media Processing Pipeline
**Goal:** Download videos, extract audio/frames

**Files to create:**
```
contentradar/
├── media/
│   ├── downloader.py     # yt-dlp wrapper
│   ├── audio.py          # ffmpeg audio extraction
│   └── frames.py         # ffmpeg frame extraction
```

**Commands:**
```bash
python3 -m contentradar download -u @divy.kairoth --outliers-only
python3 -m contentradar process -i data/downloads/ --extract audio,frames
```

**Acceptance criteria:**
- [ ] Downloads outlier videos only (save bandwidth)
- [ ] Extracts audio as MP3
- [ ] Extracts first 5 frames as JPG
- [ ] Stores in organized folder structure

---

### Phase 3: AI Analysis Pipeline
**Goal:** Transcribe + analyze content

**Files to create:**
```
contentradar/
├── analysis/
│   ├── transcribe.py     # Groq Whisper (lang=en)
│   ├── vision.py         # Gemini frame analysis
│   ├── content.py        # Claude content analysis
│   └── prompts/
│       ├── hook_analysis.txt
│       ├── retention_analysis.txt
│       └── cta_analysis.txt
```

**Commands:**
```bash
python3 -m contentradar analyze -i data/downloads/reel123/ --full
python3 -m contentradar analyze -i data/downloads/reel123/ --hooks-only
```

**Acceptance criteria:**
- [ ] Romanized transcripts (English letters)
- [ ] Hook effectiveness score (1-10)
- [ ] Retention analysis (curiosity loops)
- [ ] CTA analysis
- [ ] Replication template generation

---

### Phase 4: Swipe File Generator
**Goal:** Auto-organize insights into actionable swipe files

**Files to create:**
```
contentradar/
├── swipe/
│   ├── generator.py      # Swipe file creator
│   ├── templates/
│   │   ├── hook.md
│   │   ├── cta.md
│   │   └── tactic.md
│   └── formatter.py      # Markdown formatter
```

**Output structure:**
```
swipe-files/
├── hooks/
│   ├── question-hooks.md
│   ├── challenge-hooks.md
│   └── curiosity-hooks.md
├── ctas/
│   └── comment-ctas.md
├── tactics/
│   └── retention-tricks.md
└── index.md              # Master index
```

**Commands:**
```bash
python3 -m contentradar swipe generate -i analysis/reel123.json
python3 -m contentradar swipe list --category hooks
```

---

### Phase 5: Hypothesis Framework
**Goal:** Generate and track testable hypotheses

**Files to create:**
```
contentradar/
├── hypothesis/
│   ├── generator.py      # AI hypothesis generation
│   ├── tracker.py        # Track test results
│   └── templates/
│       └── hypothesis.md
```

**Output structure:**
```
hypotheses/
├── active/
│   └── H001-question-hooks.md
├── tested/
│   └── H002-cta-timing.md
└── learnings.md
```

**Commands:**
```bash
python3 -m contentradar hypothesis generate --from-swipe
python3 -m contentradar hypothesis test H001 --result confirmed
```

---

### Phase 6: Daily Automation
**Goal:** Hands-off monitoring via cron

**Files to create:**
```
contentradar/
├── automation/
│   ├── daily_scan.py     # Main cron script
│   ├── watchlist.py      # Creator watchlist manager
│   └── alerts.py         # Telegram notifications
├── config/
│   └── watchlist.yaml    # Creator list
```

**Cron setup:**
```bash
# 10 AM IST daily
0 4 * * * cd /path/to/contentradar && python3 -m contentradar daily-scan
```

**Commands:**
```bash
python3 -m contentradar watchlist add @divy.kairoth --platform instagram
python3 -m contentradar watchlist add @jaykapoor.24 --platform instagram
python3 -m contentradar daily-scan --dry-run
```

---

### Phase 7: GitHub Integration
**Goal:** Auto-push analysis to second-brain repo

**Files to create:**
```
contentradar/
├── storage/
│   ├── github.py         # Git operations
│   └── sync.py           # Sync manager
```

**Commands:**
```bash
python3 -m contentradar sync --push
python3 -m contentradar sync --status
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DAILY AUTOMATION FLOW                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   10:00 AM IST                                                       │
│       │                                                              │
│       ▼                                                              │
│   ┌───────────────┐                                                  │
│   │ Load Watchlist│ ──▶ config/watchlist.yaml                        │
│   │ (5 creators)  │                                                  │
│   └───────────────┘                                                  │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐     ┌───────────────┐                           │
│   │ Scrape Reels  │────▶│ Apify API     │ ──▶ ~$0.025/day           │
│   │ (50/creator)  │     │ (250 reels)   │                           │
│   └───────────────┘     └───────────────┘                           │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐                                                  │
│   │ Detect        │ ──▶ threshold=3.0, filter collabs                │
│   │ Outliers      │ ──▶ ~5-10 outliers/day                          │
│   └───────────────┘                                                  │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐     ┌───────────────┐                           │
│   │ Download      │────▶│ yt-dlp        │ ──▶ ~100MB/day            │
│   │ Outliers      │     │ (videos)      │                           │
│   └───────────────┘     └───────────────┘                           │
│           │                                                          │
│           ├──────────────────┬──────────────────┐                   │
│           ▼                  ▼                  ▼                    │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│   │ Transcribe    │  │ Extract       │  │ Vision        │          │
│   │ (Groq)        │  │ Frames        │  │ Analysis      │          │
│   │ lang=en       │  │ (ffmpeg)      │  │ (Gemini)      │          │
│   └───────────────┘  └───────────────┘  └───────────────┘          │
│           │                  │                  │                    │
│           └──────────────────┼──────────────────┘                   │
│                              ▼                                       │
│                      ┌───────────────┐                              │
│                      │ Content       │ ──▶ Claude Sonnet            │
│                      │ Analysis      │ ──▶ ~$0.10/day               │
│                      └───────────────┘                              │
│                              │                                       │
│                              ▼                                       │
│                      ┌───────────────┐                              │
│                      │ Update        │                              │
│                      │ Swipe Files   │                              │
│                      └───────────────┘                              │
│                              │                                       │
│                              ▼                                       │
│                      ┌───────────────┐                              │
│                      │ Generate      │                              │
│                      │ Hypotheses    │                              │
│                      └───────────────┘                              │
│                              │                                       │
│                              ▼                                       │
│                      ┌───────────────┐                              │
│                      │ Push to       │ ──▶ mohanagsk/second-brain   │
│                      │ GitHub        │                              │
│                      └───────────────┘                              │
│                              │                                       │
│                              ▼                                       │
│                      ┌───────────────┐                              │
│                      │ Telegram      │ ──▶ If major outlier (>10x)  │
│                      │ Alert         │                              │
│                      └───────────────┘                              │
│                                                                      │
│   DAILY COST: ~$0.15-0.20                                           │
│   MONTHLY COST: ~$5-6                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Keys Required

| Service | Key Location | Status |
|---------|--------------|--------|
| Apify | `credentials/apify-creds.env` | ✅ Configured |
| Groq | `credentials/groq-key.env` | ✅ Configured |
| Gemini | `credentials/gemini-key.env` | ✅ Configured |
| Anthropic | OpenClaw integrated | ✅ Available |
| GitHub | `credentials/github-mohanagsk.env` | ✅ Configured |

---

## Cost Projections

| Component | Daily | Monthly |
|-----------|-------|---------|
| Apify (250 reels) | $0.025 | $0.75 |
| Groq Whisper | FREE | FREE |
| Gemini Vision | FREE | FREE |
| Claude Sonnet (10 analyses) | $0.10 | $3.00 |
| Claude Opus (weekly synthesis) | $0.07 | $0.30 |
| GitHub | FREE | FREE |
| **TOTAL** | ~$0.20 | **~$4-5** |

vs Sandcastles: $39-499/mo  
vs Blort AI: $39-59/mo

---

## Success Metrics

1. **Data Quality:** >95% completeness on scraped data
2. **Transcription:** >80% readable romanized Hindi
3. **Analysis Quality:** Divy rates insights 8+/10
4. **Hypothesis Hit Rate:** >50% confirmed after testing
5. **Time Saved:** <30 min/day on content research
6. **Automation Reliability:** <1 failure/week

---

## Information Needed from Divy

1. **Watchlist:** Which 5-10 creators to monitor daily?
   - @divy.kairoth (self)
   - @jaykapoor.24
   - @vedikabhaia
   - Others?

2. **Alert Threshold:** What outlier score triggers Telegram alert?
   - Current suggestion: >10x average

3. **TikTok Priority:** Phase 4 is TikTok — build it or skip?

4. **Swipe File Format:** Notion sync or pure GitHub markdown?

5. **Build Approach:**
   - Option A: Add to existing `contentradar/` repo (extend Phase 1)
   - Option B: New repo `contentradar-v2/` (fresh start with GSD)

6. **Timeline Expectation:** MVP in 1 week or polish over 2 weeks?

---

## Next Steps

1. [ ] Get watchlist from Divy
2. [ ] Confirm build approach (extend vs new repo)
3. [ ] Start Phase 1 (Instagram scraping module)
4. [ ] Run the apify actor comparison test
5. [ ] Set up GSD structure if using new repo

---

*PRD based on 6 parallel agent tests, competitor analysis, and challenger critique.*
