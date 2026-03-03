# Instagram Intel System — System Design Document

**Created:** March 3, 2026  
**Status:** Design Phase  
**Author:** Mohana

---

## 🎯 SYSTEM GOALS

1. **Scrape** — Fetch metadata + videos from Instagram reels
2. **Transcribe** — Convert audio to text (including Hindi)
3. **Visual Analysis** — Extract frames, detect hooks, text overlays
4. **Pattern Detection** — Find what works, build swipe files
5. **Failure Analysis** — Track what didn't work
6. **Daily Automation** — Monitor creators, detect outliers
7. **Storage** — GitHub-based knowledge base

---

## 📊 SYSTEM ARCHITECTURE

```mermaid
flowchart TB
    subgraph INPUT["📥 INPUT"]
        CL[Creator List]
        RI[Reel URLs]
    end

    subgraph SCRAPING["🔍 SCRAPING LAYER"]
        IL[Instaloader<br/>FREE]
        YT[yt-dlp<br/>FREE]
        AP[Apify<br/>$2.60/1K]
        
        IL -->|rate limited| YT
        YT -->|rate limited| AP
    end

    subgraph DOWNLOAD["⬇️ DOWNLOAD LAYER"]
        DL_YT[yt-dlp Download]
        DL_IL[Instaloader Download]
    end

    subgraph PROCESSING["⚙️ PROCESSING LAYER"]
        subgraph AUDIO["🎵 Audio Pipeline"]
            FF_A[ffmpeg extract audio]
            GW[Groq Whisper<br/>FREE]
            FW[faster-whisper<br/>FREE/Local]
        end
        
        subgraph VIDEO["🎬 Video Pipeline"]
            FF_V[ffmpeg extract frames]
            GV[Gemini Vision<br/>FREE/GCP]
            CV[Claude Vision<br/>$0.01/img]
        end
    end

    subgraph ANALYSIS["📈 ANALYSIS LAYER"]
        OD[Outlier Detection<br/>Python]
        PA[Pattern Analysis<br/>AI]
        HA[Hook Analysis<br/>AI]
        FA[Failure Analysis<br/>AI]
    end

    subgraph OUTPUT["📤 OUTPUT"]
        subgraph SWIPE["📁 Swipe Files"]
            SF_H[Best Hooks]
            SF_M[Best Music]
            SF_T[Best Tactics]
        end
        
        subgraph LOGS["📋 Logs"]
            FL[Failure Log]
            OL[Outlier Log]
            TL[Trend Log]
        end
        
        GH[GitHub Storage]
        TG[Telegram Alerts]
    end

    subgraph AUTOMATION["🔄 AUTOMATION"]
        DC[Daily Cron<br/>10 AM IST]
        WC[Weekly Digest]
    end

    INPUT --> SCRAPING
    SCRAPING --> DOWNLOAD
    DOWNLOAD --> PROCESSING
    PROCESSING --> ANALYSIS
    ANALYSIS --> OUTPUT
    AUTOMATION --> SCRAPING
```

---

## 🔧 COMPONENT BREAKDOWN

### Layer 1: Scraping

```mermaid
flowchart LR
    subgraph SCRAPING_OPTIONS["Scraping Options"]
        direction TB
        A[Instaloader] -->|"✅ FREE<br/>❌ Rate limits<br/>⭐ Quality: 8/10"| OUT
        B[yt-dlp] -->|"✅ FREE<br/>❌ Limited metadata<br/>⭐ Quality: 6/10"| OUT
        C[Apify] -->|"❌ $2.60/1K<br/>✅ Reliable<br/>⭐ Quality: 10/10"| OUT
        OUT[Metadata + URLs]
    end
```

| Tool | Cost | Rate Limits | Metadata Quality | Video URLs | Score |
|------|------|-------------|------------------|------------|-------|
| Instaloader | FREE | Yes (IG) | High | Yes | ?/100 |
| yt-dlp | FREE | Minimal | Medium | Yes | ?/100 |
| Apify | $2.60/1K | No | Very High | Yes | ?/100 |

### Layer 2: Download

```mermaid
flowchart LR
    subgraph DOWNLOAD_OPTIONS["Download Options"]
        A[yt-dlp] -->|"✅ FREE<br/>✅ Fast<br/>⭐ Quality: 9/10"| OUT
        B[Instaloader] -->|"✅ FREE<br/>❌ Slower<br/>⭐ Quality: 8/10"| OUT
        OUT[Video Files]
    end
```

### Layer 3: Transcription

```mermaid
flowchart LR
    subgraph TRANSCRIPTION["Transcription Options"]
        A[Groq Whisper] -->|"✅ FREE<br/>✅ Fast<br/>✅ Hindi support<br/>⭐ 9/10"| OUT
        B[faster-whisper] -->|"✅ FREE<br/>❌ Needs RAM<br/>✅ Hindi support<br/>⭐ 7/10"| OUT
        C[OpenAI Whisper] -->|"❌ $0.006/min<br/>✅ Best quality<br/>⭐ 10/10"| OUT
        OUT[Transcript Text]
    end
```

### Layer 4: Visual Analysis

```mermaid
flowchart LR
    subgraph VISUAL["Visual Analysis Options"]
        A[Gemini Vision] -->|"✅ FREE (GCP)<br/>⭐ 8/10"| OUT
        B[Claude Vision] -->|"❌ $0.01/img<br/>⭐ 10/10"| OUT
        C[GPT-4V] -->|"❌ $0.01/img<br/>⭐ 9/10"| OUT
        OUT[Visual Insights]
    end
```

### Layer 5: Analysis

**What we're analyzing:**

| Category | Metrics | Output |
|----------|---------|--------|
| **Hook Analysis** | First 3 sec, opening line, visual hook | Swipe file |
| **Success Patterns** | Outlier score, engagement rate, virality | Pattern table |
| **Music/Audio** | Trending sounds, music choices | Music swipe |
| **Tactics** | CTAs, text overlays, pacing | Tactics log |
| **Failures** | Low performers, what didn't work | Failure log |
| **Trends** | What's working THIS week | Trend log |

---

## 📁 GITHUB STORAGE STRUCTURE

```
mohanagsk/second-brain/
└── areas/
    └── instagram/
        ├── PLANNING.md
        ├── SYSTEM_DESIGN.md
        ├── analysis/
        │   ├── data/           # Raw JSON data
        │   └── reports/        # Markdown reports
        ├── swipe-files/
        │   ├── hooks.md        # Best hooks
        │   ├── music.md        # Best music/sounds
        │   └── tactics.md      # Best tactics
        ├── logs/
        │   ├── failures.md     # What didn't work
        │   ├── outliers.md     # Outlier tracking
        │   └── trends.md       # Weekly trends
        └── creators/
            ├── divy.kairoth.md
            ├── vedikabhaia.md
            └── jaykapoor.24.md
```

---

## 🔄 DAILY AUTOMATION FLOW

```mermaid
sequenceDiagram
    participant Cron as Daily Cron (10 AM)
    participant Scraper as Scraping Layer
    participant Processor as Processing Layer
    participant Analyzer as Analysis Layer
    participant GitHub as GitHub Storage
    participant Telegram as Telegram Alert

    Cron->>Scraper: Trigger daily fetch
    loop For each creator in list
        Scraper->>Scraper: Fetch new reels (last 24h)
        Scraper->>Processor: Send new reels
        Processor->>Processor: Download + Transcribe + Frames
        Processor->>Analyzer: Send processed data
        Analyzer->>Analyzer: Detect outliers
        Analyzer->>Analyzer: Update swipe files
        Analyzer->>GitHub: Push updates
        alt Outlier detected
            Analyzer->>Telegram: Alert with analysis
        end
    end
```

---

## 🧪 TESTING PLAN

### Test 1: Scraping Comparison
**Goal:** Score Instaloader vs yt-dlp vs Apify

| Metric | Weight |
|--------|--------|
| Success rate | 30% |
| Speed | 20% |
| Metadata quality | 25% |
| Cost | 25% |

**Test data:** 10 reels from @divy.kairoth

### Test 2: Download Comparison
**Goal:** Score yt-dlp vs Instaloader for downloading

| Metric | Weight |
|--------|--------|
| Success rate | 40% |
| Speed | 30% |
| Quality | 30% |

**Test data:** 10 reels

### Test 3: Transcription Quality
**Goal:** Verify Groq Whisper works for Hindi

| Metric | Weight |
|--------|--------|
| Accuracy (Hindi) | 50% |
| Speed | 25% |
| Cost | 25% |

**Test data:** 5 Hindi reels

### Test 4: Vision Analysis
**Goal:** Compare Gemini vs Claude for visual analysis

| Metric | Weight |
|--------|--------|
| Hook detection | 30% |
| Text extraction | 25% |
| Scene analysis | 25% |
| Cost | 20% |

**Test data:** 5 reels with text overlays

---

## 🔍 EXISTING TOOLS RESEARCH

### ClawHub Skills to Inspect

| Skill | What it does | Useful for |
|-------|--------------|------------|
| `instagram-analyzer` | Engagement metrics | Scraping |
| `instagram-search` | Search functionality | Discovery |
| `faster-whisper-transcribe` | Local transcription | Audio |
| `assemblyai-transcribe` | Cloud transcription | Audio |

### GitHub Repos to Check

| Repo | What it does |
|------|--------------|
| `instaloader/instaloader` | Official scraper |
| `yt-dlp/yt-dlp` | Video downloader |
| `Avnsh1111/Instagram-Reels-Scraper` | Reels + analytics |

---

## ❓ INFORMATION NEEDED

1. **Instagram session** — For Instaloader (may need login cookies)
2. **Groq API key** — Already have ✅
3. **Gemini API** — Already have ✅
4. **Claude Vision** — Part of existing subscription?
5. **Creator list** — Starting with: divy.kairoth, vedikabhaia, jaykapoor.24

---

## 📋 NEXT STEPS

1. [ ] Finalize this system design (get approval)
2. [ ] Inspect ClawHub skills (without installing)
3. [ ] Spawn parallel agents for tool comparison tests
4. [ ] Calculate scores for each tool
5. [ ] Build final optimized pipeline
6. [ ] Set up daily automation

---

*Document will be updated as tests complete*
