# PROJECT.md — ContentRadar Instagram Intel

**Status:** AWAITING VERIFICATION  
**Method:** Get Shit Done (GSD) spec-driven development

---

## 🎯 Vision

Build a free/cheap Instagram content intelligence system that:
1. Finds viral outliers from competitors
2. Breaks down WHY they worked (hooks, loops, CTAs, audio)
3. Builds swipe files with actionable templates
4. Creates testable hypotheses
5. Runs daily on autopilot

**Replace:** Sandcastles.ai ($39-499/mo), Blort AI ($39-59/mo)  
**Cost Target:** <$10/mo

---

## 🔍 Research Complete

### Competitor Analysis
| Tool | Price | Key Feature | Gap |
|------|-------|-------------|-----|
| Sandcastles.ai | $39-499/mo | Script generation | No Hindi, expensive |
| Blort AI | $39-59/mo | Frame-by-frame analysis | New, no API |
| OpusClip | $0-29/mo | Virality score (0-99) | YouTube/TikTok only |
| TubeBuddy/vidIQ | $0-49/mo | YouTube SEO | No Instagram |

**Major Gap:** Instagram has 2B users, 500M daily Reels — NO specialized tools exist.

### Technical Decisions (Tested)
| Component | Winner | Why |
|-----------|--------|-----|
| Scraping | Apify (apidojo) | Only tool with views, $0.50/1K |
| Download | yt-dlp | 100% success, free |
| Transcription | Groq Whisper `lang=en` | Romanized Hindi, free |
| Vision | Gemini | Free via GCP |
| Analysis | Claude Sonnet | Best value ($0.01/analysis) |
| Deep Analysis | Claude Opus | Weekly synthesis |

### Unbiased Analysis Validation
- **3/5 exact predictions** without knowing view counts
- Framework correctly identified top performers
- Need to add: emotional resonance, trust factor scoring

---

## 📋 Requirements

### Must Have (v1)
1. Scrape last 100 posts from creator (Apify)
2. Detect outliers (>3x avg, with collab filtering)
3. Download outlier videos (yt-dlp)
4. Transcribe to romanized text (Groq, lang=en)
5. Extract visual hooks (Gemini, first 5 frames)
6. Analyze content (Claude Sonnet)
7. Save to swipe files (hooks, CTAs, loops)
8. Daily automation via cron
9. GitHub push for storage

### Should Have (v1.1)
10. Trending audio tracking
11. Curiosity loop detection (7 types)
12. Hypothesis generation & tracking
13. A/B model performance tracking
14. Telegram alerts for major outliers (>10x)

### Could Have (v2)
15. Weighted hypothesis scoring (predict before posting)
16. Multi-creator comparison reports
17. Weekly digest emails
18. Web dashboard

### Won't Have (out of scope)
- TikTok support (Phase 4 later)
- YouTube support (already have ContentRadar v1)
- Script generation (maybe v3)
- Brand/enterprise features (separate product)

---

## 🗺️ Roadmap

### Phase 1: Core Scraping + Outlier Detection
- [ ] Apify integration (100 posts)
- [ ] Outlier scoring (avg from 100, 3-4 day half-life)
- [ ] Duplicate detection (same reel, different URLs)
- [ ] Collaboration filtering
- [ ] CLI: `python scan @username`

### Phase 2: Media Processing
- [ ] yt-dlp download (outliers only)
- [ ] ffmpeg audio extraction
- [ ] ffmpeg frame extraction (first 5)
- [ ] Storage management (delete after analysis)

### Phase 3: AI Analysis
- [ ] Groq Whisper transcription (lang=en)
- [ ] Gemini vision analysis
- [ ] Claude content analysis
- [ ] Curiosity loop detection
- [ ] Hook scoring
- [ ] CTA analysis

### Phase 4: Swipe Files
- [ ] Auto-generate entries from analysis
- [ ] Hook library (table format)
- [ ] Visual hooks
- [ ] CTA patterns
- [ ] Trending audio log

### Phase 5: Hypothesis Framework
- [ ] Generate hypotheses from patterns
- [ ] Track test results
- [ ] Update weights based on outcomes
- [ ] Confidence scoring

### Phase 6: Daily Automation
- [ ] Cron setup (10 AM IST)
- [ ] Watchlist config
- [ ] GitHub auto-push
- [ ] Telegram alerts

---

## 💰 Cost Analysis

| Component | Monthly |
|-----------|---------|
| Apify (500 reels) | $0.25 |
| Groq Whisper | FREE |
| Gemini Vision | FREE |
| Claude Sonnet (100 analyses) | ~$1.00 |
| Claude Opus (4 weekly) | ~$0.30 |
| GitHub | FREE |
| **TOTAL** | **~$1.55/mo** |

(Using existing Claude subscription covers most of this)

---

## ❓ Questions for Divy

1. **Watchlist:** Confirm creators to monitor daily?
   - @divy.kairoth ✅
   - @jaykapoor.24 ✅
   - @vedikabhaia ✅
   - Others?

2. **Alert threshold:** >10x for Telegram notification?

3. **Storage:** Keep videos after analysis or delete?

4. **Swipe file location:** GitHub (second-brain) or Notion?

5. **When to build:** After you verify this plan?

---

## 📁 Research Documents Available

| Document | Location | Size |
|----------|----------|------|
| Competitor Deep Dive | `COMPETITOR_DEEP_DIVE.md` | 33KB |
| Brand Market Analysis | `research/BRAND_MARKET_ANALYSIS.md` | 30KB |
| Clip Tools Research | `research/CLIP_TOOLS_RESEARCH.md` | 25KB |
| Unbiased Analysis | `tests/UNBIASED_ANALYSIS.md` | 18KB |
| Model Comparison | `tests/analysis_model_comparison.md` | 17KB |
| Romanization Test | `tests/romanization_comparison.md` | 11KB |

---

## 📐 Design Documents Available

| Design | Location | Purpose |
|--------|----------|---------|
| Curiosity Loop Detection | `design/CURIOSITY_LOOP_DETECTION.md` | 7 loop types, algorithm |
| Trending Audio Analysis | `design/TRENDING_AUDIO_ANALYSIS.md` | Track trending sounds |
| A/B Model Tracking | `design/AB_MODEL_TRACKING.md` | Score models over time |
| Weighted Hypothesis | `design/WEIGHTED_HYPOTHESIS_SCORING.md` | Predict virality |

---

## 📝 Swipe Templates Ready

| Template | Size |
|----------|------|
| HOOK_LIBRARY.md | 6KB |
| VISUAL_HOOKS.md | 11KB |
| CTA_PATTERNS.md | 13KB |
| CURIOSITY_LOOPS.md | 16KB |

---

**STATUS: READY FOR YOUR VERIFICATION**

Reply with:
- ✅ Approved — start building
- 🔄 Changes needed — [specify what]
- ❓ Questions — [ask away]
