# Instagram Intel — Master Plan v1

**Created:** March 3, 2026  
**Status:** DRAFT — Needs challenger review  
**Author:** Mohana

---

## 🎯 CORE GOAL

Build a complete Instagram content intelligence system that:
1. Finds outlier content reliably
2. Understands WHY it worked (hooks, patterns, tactics)
3. Builds a swipe file of proven elements
4. Creates testable hypotheses for new content
5. Runs on autopilot with minimal cost

---

## 📋 PHASE BREAKDOWN

### Phase A: Data Collection Testing
**Goal:** Find the most reliable + cheapest scraping method

| Test | Actors to Compare | Data Points |
|------|-------------------|-------------|
| A.1 | apidojo vs apify-official vs hpix | Same 50 reels |
| A.2 | Measure: cost, speed, data completeness, view accuracy | Side-by-side |
| A.3 | Reliability: run 3x, check consistency | Same data |

**Output:** Scored comparison, winner selected

### Phase B: Transcription Testing
**Goal:** Get accurate ROMANIZED transcripts (English font, any language)

| Test | Tools to Compare |
|------|------------------|
| B.1 | Groq Whisper (romanize=true?) |
| B.2 | Groq Whisper + post-process to romanize |
| B.3 | OpenAI Whisper API (if needed) |
| B.4 | Google Speech-to-Text (romanization support) |

**Key requirement:** Output must be "kya scene hai" NOT "क्या सीन है"

**Output:** Best tool for romanized Hindi transcripts

### Phase C: Vision Analysis Testing
**Goal:** Extract visual hooks, text overlays, scene composition

| Test | Models to Compare |
|------|-------------------|
| C.1 | Gemini 1.5 Pro Vision (FREE via GCP) |
| C.2 | Claude Vision (existing subscription) |
| C.3 | GPT-4V (if budget allows) |

**What to extract:**
- First 3 frames (visual hook)
- Text overlays (what text appears)
- Scene composition (talking head? B-roll? Split screen?)
- Pacing (cuts per second)
- Thumbnail quality

**Output:** Scored comparison, best model selected

### Phase D: Content Analysis Testing
**Goal:** Understand WHY content worked

| Test | Models to Compare |
|------|-------------------|
| D.1 | Claude Opus (deep analysis) |
| D.2 | Claude Sonnet (faster, cheaper) |
| D.3 | GPT-4 Turbo |
| D.4 | Gemini 1.5 Pro |
| D.5 | Combined approach (run all, synthesize) |

**Analysis dimensions:**
1. Hook effectiveness (first 3 seconds)
2. Curiosity loops (what makes you keep watching)
3. Storytelling structure (problem → solution? Before/after?)
4. CTA effectiveness (comment X to get Y)
5. Emotional triggers (FOMO, curiosity, humor)
6. Pattern matching (what's similar to other outliers)

**Output:** Best model + prompt for each dimension

### Phase E: Swipe File Architecture
**Goal:** Store actionable patterns, not just raw data

```
swipe-files/
├── hooks/
│   ├── question-hooks.md      # "Kya tumhe pata hai..."
│   ├── challenge-hooks.md     # "Bet you can't..."
│   ├── curiosity-hooks.md     # "This one trick..."
│   └── controversy-hooks.md   # Hot takes
├── structures/
│   ├── problem-solution.md
│   ├── before-after.md
│   ├── listicle.md
│   └── story-arc.md
├── tactics/
│   ├── cta-patterns.md        # Comment X for Y
│   ├── engagement-hacks.md
│   └── retention-tricks.md
├── visuals/
│   ├── thumbnail-styles.md
│   ├── text-overlay-patterns.md
│   └── editing-styles.md
└── music/
    ├── trending-sounds.md
    └── mood-categories.md
```

**Each entry includes:**
- Example reel URL
- Transcript excerpt
- Why it worked (hypothesis)
- Performance metrics
- How to replicate

### Phase F: Hypothesis Testing Framework
**Goal:** Build → Test → Learn cycle

```
hypothesis/
├── active/
│   ├── H001-question-hooks-perform-3x.md
│   └── H002-cta-in-first-5s-doubles-comments.md
├── tested/
│   ├── H001-CONFIRMED.md
│   └── H003-REJECTED.md
└── insights/
    └── learnings.md
```

**Hypothesis format:**
```markdown
# H001: Question hooks perform 3x better

## Hypothesis
Reels starting with a question get 3x more engagement than statement hooks.

## Evidence
- @divy.kairoth: 5/7 outliers use question hooks
- @vedikabhaia: 4/6 outliers use question hooks

## Test Plan
1. Create 2 versions of same content
2. A: Question hook, B: Statement hook
3. Post at same time, same day
4. Measure after 48h

## Results
[To be filled after test]

## Conclusion
[Confirmed/Rejected/Needs more data]
```

### Phase G: Multi-Model Synthesis
**Goal:** Combine insights from multiple AI models

**Approach:**
```
Raw Content
    ↓
┌───────────────────────────────────┐
│     PARALLEL ANALYSIS             │
├───────────────────────────────────┤
│ Claude Opus → Deep reasoning      │
│ Gemini 1.5 → Pattern matching     │
│ GPT-4 → Creative angles           │
│ Sonnet → Quick categorization     │
└───────────────────────────────────┘
    ↓
SYNTHESIS LAYER (Claude Opus)
    ↓
Combined insights + confidence scores
    ↓
Swipe file entry
```

**Why multiple models:**
- Each has different strengths
- Reduces blind spots
- Higher confidence when they agree
- Interesting when they disagree (explore why)

### Phase H: Daily Automation
**Goal:** Hands-off monitoring

```
Daily Cron (10 AM IST)
    ↓
1. Fetch new reels from watchlist (Apify)
2. Detect outliers (>3x average)
3. Download outlier videos (yt-dlp)
4. Transcribe (Groq, romanized)
5. Extract frames (ffmpeg)
6. Run vision analysis (Gemini)
7. Run content analysis (Claude)
8. Update swipe files
9. Generate hypotheses
10. Push to GitHub
11. Alert on Telegram (if major outlier)
```

---

## 🔍 GAPS & QUESTIONS

### Known Gaps
1. **Romanization:** How to force Groq Whisper to output in English font?
2. **Cost tracking:** How to track API costs across all services?
3. **Model disagreement:** What if models give conflicting analysis?
4. **False positives:** How to filter out paid promotions / ads?
5. **Seasonality:** How to account for trending topics vs evergreen patterns?

### Questions for Challenger Agent
1. Is multi-model synthesis overkill? Would single model + better prompts work?
2. Are we missing any content dimensions (music? posting time? hashtags?)
3. Is the swipe file structure right? Too granular? Not enough?
4. How do we measure if our hypotheses are actually useful?
5. What's the minimum viable version of this system?

---

## 🏁 IMMEDIATE NEXT STEPS

1. [ ] **Spawn challenger agent** to review this plan
2. [ ] **Test Apify actors** (apidojo vs official vs hpix) on same 20 reels
3. [ ] **Test romanization** methods for transcripts
4. [ ] **Test vision models** on 5 reels with text overlays
5. [ ] **Test analysis models** with same prompt across 4 models
6. [ ] **Build swipe file structure** in GitHub
7. [ ] **Create first 3 hypotheses** from existing outlier data

---

## 💰 COST PROJECTIONS

| Component | Monthly Volume | Cost |
|-----------|---------------|------|
| Apify (apidojo) | 500 reels | ~$0.25 |
| Groq Whisper | 500 transcripts | FREE |
| Gemini Vision | 500 × 5 frames | FREE (GCP) |
| Claude analysis | 100 deep analyses | ~$5 (existing sub) |
| GitHub storage | Unlimited text | FREE |
| **TOTAL** | | **~$5.25/mo** |

vs Sandcastles: $39-499/mo

---

## 📊 SUCCESS METRICS

1. **Data quality:** >95% completeness on scraped data
2. **Transcript accuracy:** >80% readable (romanized)
3. **Analysis usefulness:** Divy rates 8/10+ on insights
4. **Hypothesis hit rate:** >50% confirmed after testing
5. **Time saved:** <30 min/day on content research (vs hours)

---

*This plan is DRAFT. Awaiting challenger review before execution.*
