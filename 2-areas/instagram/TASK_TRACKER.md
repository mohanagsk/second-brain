# ContentRadar v2 — Task Tracker

**Created:** March 3, 2026  
**Status:** IN PROGRESS

---

## 📋 MASTER TASK LIST

### RESEARCH & ANALYSIS

- [ ] **R1.** Research Vidyo.ai — AI clip extraction methodology
- [ ] **R2.** Research OpusClip — Viral moment detection approach
- [ ] **R3.** Research TubeBuddy/vidIQ technical architecture (public APIs)
- [ ] **R4.** Spawn parallel agent for brand/enterprise market analysis
- [ ] **R5.** Create unbiased analysis agent (no view counts given)

### SYSTEM DESIGN

- [ ] **S1.** Update system design — remove GPT-4, use only Claude Sonnet/Opus
- [ ] **S2.** Update system design — add Gemini 3 Pro (not 1.5)
- [ ] **S3.** Update system design — add ffmpeg for media processing
- [ ] **S4.** Update system design — add trending audio analysis
- [ ] **S5.** Design curiosity loop detection algorithm
- [ ] **S6.** Design weighted hypothesis scoring system

### SWIPE FILE STRUCTURE

- [ ] **F1.** Create hook template library (separate file, tables format)
- [ ] **F2.** Add visual hooks to swipe files (not just transcript)
- [ ] **F3.** Add CTA patterns to swipe files
- [ ] **F4.** Design A/B model tracking format

### IMPLEMENTATION

- [ ] **I1.** Build Instagram scraping module (Apify, 100 posts)
- [ ] **I2.** Build outlier detection (avg of 100 posts, 3-4 day half-life)
- [ ] **I3.** Build media pipeline (ffmpeg frames + audio)
- [ ] **I4.** Build transcription (Groq Whisper, lang=en)
- [ ] **I5.** Build vision analysis (Gemini)
- [ ] **I6.** Build content analysis (Claude Sonnet)
- [ ] **I7.** Build daily automation script
- [ ] **I8.** Fix duplicate detection (Trial vs Unboxify same reel)

### QUESTIONS FOR DIVY

- [ ] **Q1.** Confirm watchlist creators beyond @divy.kairoth, @jaykapoor.24, @vedikabhaia?
- [ ] **Q2.** Alert threshold for Telegram (>5x? >10x?)?

---

## 🔄 EXECUTION LOG

| Time | Task | Status |
|------|------|--------|
| 19:10 | Starting R1-R3 research | 🔄 |
| 19:08 | S5. Curiosity loop detection algorithm | ✅ |
| 19:12 | S4. Trending audio analysis design | ✅ |
| 19:14 | A/B Model tracking design | ✅ |
| 19:15 | Weighted hypothesis scoring design | ✅ |
| 19:40 | Spawned 6 parallel agents | 🔄 |
| | | |

## ANSWERS TO DIVY'S QUESTIONS

### Q: Using subscription plan for analysis? Cost part of that?
**A:** Yes, Claude Sonnet/Opus analysis uses your existing OpenClaw subscription. The ~$5/mo estimate is for:
- Apify scraping ($0.75/mo)
- Extra Claude calls beyond normal usage (~$3-4/mo)
Your main Claude subscription covers most analysis.

### Q: Why not Gemini 3 Pro?
**A:** You're right — will use latest Gemini model available (Gemini 2.0 or 3.0 if released). Updated in system design.

### Q: Where did GPT-4 come from? No API key given.
**A:** Removed GPT-4 from pipeline. Will use only:
- Claude Sonnet (daily analysis)
- Claude Opus (weekly deep dives)
- Gemini (vision analysis - free via GCP)

### Q: Trial and Unboxify same reel?
**A:** Yes, this was a duplicate detection bug. Will add deduplication by reel ID in scraping module.

### Q: Half-life 3-4 days assumption?
**A:** Confirmed. Using views as outlier representation since most engagement happens in first 3-4 days. Avg calculated from 100 most recent posts.

