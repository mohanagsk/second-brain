# ROADMAP.md — ContentRadar Instagram Intel

**Method:** Get Shit Done (GSD)  
**Status:** AWAITING APPROVAL

---

## Phase Overview

| Phase | Name | Duration | Dependencies |
|-------|------|----------|--------------|
| 1 | Core Scraping | 2-3 hours | None |
| 2 | Media Processing | 1-2 hours | Phase 1 |
| 3 | AI Analysis | 2-3 hours | Phase 2 |
| 4 | Swipe File Automation | 1 hour | Phase 3 |
| 5 | Hypothesis System | 1-2 hours | Phase 4 |
| 6 | Daily Automation | 1 hour | All above |

**Total Estimate:** 8-12 hours of development

---

## Phase 1: Core Scraping

### Goal
Build Instagram scraping module with Apify integration and outlier detection.

### Tasks
- [ ] 1.1 Create `src/scraper.py` — Apify API wrapper
- [ ] 1.2 Create `src/outlier.py` — Outlier detection logic
- [ ] 1.3 Create `src/cli.py` — Command line interface
- [ ] 1.4 Create `config/watchlist.yaml` — Creator list
- [ ] 1.5 Add duplicate detection (same reel, diff URL)
- [ ] 1.6 Add collaboration filtering (optional flag)
- [ ] 1.7 Test on @divy.kairoth, @jaykapoor.24, @vedikabhaia

### Deliverables
```bash
python -m contentradar scan instagram -u @divy.kairoth
python -m contentradar scan instagram -u @divy.kairoth --outliers-only
python -m contentradar scan instagram -u @divy.kairoth --filter-collabs
```

### Acceptance
- ✅ Returns 100 posts with views, likes, comments
- ✅ Correctly identifies outliers (>3x avg)
- ✅ No duplicate reels in output
- ✅ Saves to `data/raw/` and `data/outliers/`

---

## Phase 2: Media Processing

### Goal
Download videos and extract audio/frames for analysis.

### Tasks
- [ ] 2.1 Create `src/media.py` — ffmpeg wrapper
- [ ] 2.2 Implement video download (yt-dlp)
- [ ] 2.3 Implement audio extraction (MP3)
- [ ] 2.4 Implement frame extraction (first 5 JPGs)
- [ ] 2.5 Add cleanup function (delete after analysis)
- [ ] 2.6 Test on 5 sample reels

### Deliverables
```bash
python -m contentradar download reel_url
python -m contentradar process --extract audio,frames
```

### Acceptance
- ✅ Downloads video successfully
- ✅ Extracts clear audio
- ✅ Extracts 5 frames at 0s, 1s, 2s, 3s, 4s
- ✅ Cleanup removes temp files

---

## Phase 3: AI Analysis

### Goal
Transcribe audio and analyze content with AI models.

### Tasks
- [ ] 3.1 Create `src/transcribe.py` — Groq Whisper wrapper
- [ ] 3.2 Create `src/vision.py` — Gemini vision analysis
- [ ] 3.3 Create `src/analyze.py` — Claude content analysis
- [ ] 3.4 Create `src/prompts/` — Analysis prompt templates
- [ ] 3.5 Implement curiosity loop detection (7 types)
- [ ] 3.6 Implement hook scoring (1-10)
- [ ] 3.7 Implement CTA analysis
- [ ] 3.8 Test on 5 sample reels (compare to manual analysis)

### Deliverables
```bash
python -m contentradar transcribe reel_id
python -m contentradar analyze reel_id --full
python -m contentradar analyze reel_id --hooks-only
```

### Acceptance
- ✅ Transcripts are romanized (English letters)
- ✅ Vision extracts text overlays correctly
- ✅ Content analysis matches manual review
- ✅ Curiosity loops detected with >70% accuracy

---

## Phase 4: Swipe File Automation

### Goal
Auto-generate swipe file entries from analysis.

### Tasks
- [ ] 4.1 Create `src/swipe.py` — Swipe file generator
- [ ] 4.2 Define entry templates (hooks, CTAs, loops)
- [ ] 4.3 Implement auto-append to existing files
- [ ] 4.4 Add deduplication (don't add same pattern twice)
- [ ] 4.5 Add confidence scoring (based on outlier score)
- [ ] 4.6 Test with 10 analyzed reels

### Deliverables
```bash
python -m contentradar swipe generate --from-analysis
python -m contentradar swipe list --category hooks
```

### Acceptance
- ✅ New patterns appended to correct files
- ✅ Table format maintained
- ✅ No duplicate entries
- ✅ Confidence scores included

---

## Phase 5: Hypothesis System

### Goal
Generate and track testable hypotheses from patterns.

### Tasks
- [ ] 5.1 Create `src/hypothesis.py` — Hypothesis generator
- [ ] 5.2 Create `hypotheses/` folder structure
- [ ] 5.3 Implement hypothesis generation from swipe patterns
- [ ] 5.4 Implement test tracking (confirmed/rejected)
- [ ] 5.5 Implement weight updates based on outcomes
- [ ] 5.6 Create weekly report generator

### Deliverables
```bash
python -m contentradar hypothesis generate
python -m contentradar hypothesis test H001 --result confirmed
python -m contentradar hypothesis report
```

### Acceptance
- ✅ Hypotheses generated with clear test criteria
- ✅ Weights update when tests complete
- ✅ Weekly report shows performance trends

---

## Phase 6: Daily Automation

### Goal
Set up hands-off daily monitoring.

### Tasks
- [ ] 6.1 Create `src/daily_scan.py` — Main orchestrator
- [ ] 6.2 Implement watchlist loading
- [ ] 6.3 Implement GitHub push
- [ ] 6.4 Implement Telegram alerts
- [ ] 6.5 Create cron setup script
- [ ] 6.6 Test full pipeline end-to-end

### Deliverables
```bash
python -m contentradar daily-scan
python -m contentradar daily-scan --dry-run
```

### Cron
```bash
# 10 AM IST = 4:30 AM UTC
30 4 * * * cd ~/instagram-intel && python -m contentradar daily-scan
```

### Acceptance
- ✅ Full pipeline runs without errors
- ✅ Results pushed to GitHub
- ✅ Telegram alert sent for >10x outliers
- ✅ Completes in <10 minutes for 5 creators

---

## Post-MVP Phases

### Phase 7: Trending Audio (v1.1)
- Track audio across all scraped reels
- Identify trending sounds
- Weekly audio report

### Phase 8: A/B Model Tracking (v1.1)
- Track which AI models predict best
- Update model selection based on accuracy
- Monthly model performance report

### Phase 9: Pre-Publish Scoring (v2)
- Score content BEFORE posting
- Use hypothesis weights to predict
- Suggest improvements

---

## Timeline

| Week | Focus |
|------|-------|
| Week 1 | Phases 1-3 (scraping + analysis) |
| Week 2 | Phases 4-6 (swipe + automation) |
| Week 3 | Testing + bug fixes |
| Week 4 | V1.1 features (audio, model tracking) |

---

**AWAITING DIVY'S APPROVAL TO BEGIN**
