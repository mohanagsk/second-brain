# Clip & Video Analysis Tools Research

**Date:** March 3, 2026  
**Purpose:** Understand how competitors detect viral moments and extract clips

---

## 1. Vidyo.ai (Now Quso.ai)

**Website:** https://quso.ai (rebranded from vidyo.ai)  
**Tagline:** "All-in-one Social Media AI Marketing Team"

### Core Features
- AI video clipping from long-form content
- Auto-captioning
- AI editing and repurposing
- Social media scheduling
- Multi-platform management

### How It Works
1. Upload long-form video
2. AI analyzes content for "viral-worthy" moments
3. Auto-generates clips with captions
4. Suggests best posting times

### Technical Approach (Inferred)
- **Speech-to-text:** For transcript analysis
- **Sentiment peaks:** Detects emotional high points
- **Engagement signals:** Looks for questions, hooks, reveals
- **Pacing analysis:** Identifies fast-paced segments

### Pricing
- Part of quso.ai suite (~$49-69/mo for repurposing)
- Replaces multiple tools: Podsqueeze, Podcastle, etc.
- Claims to save $451/mo vs separate tools

### API
- Not publicly documented
- Enterprise integrations available

### What We Can Steal
1. **Sentiment peak detection** — Find emotional high points
2. **Auto-caption generation** — Already doing with Whisper
3. **Multi-platform formatting** — Aspect ratio auto-resize

---

## 2. OpusClip

**Website:** https://opus.pro  
**Tagline:** "#1 AI video clipping tool to create viral shorts"  
**Users:** 12M+ creators and businesses

### Core Features

#### ClipAnything
- Works on ANY genre (not just podcasts)
- Vlogs, gaming, sports, interviews, explainers
- "Viral clips in 1 click"

#### ReframeAnything
- Auto-resize for any platform
- AI object tracking (keeps subjects centered)
- Manual tracking override

#### AI Editor
- Full control or let AI take over
- Brand templates (font, color, logo, intro/outro)
- Team workspace

### How It Works (Technical)
1. **Transcript analysis:** Identifies key moments via NLP
2. **Virality scoring:** Proprietary algorithm scores segments
3. **Object tracking:** Computer vision for reframing
4. **Engagement prediction:** ML model trained on viral content

### Key Innovation: Virality Score
OpusClip assigns each clip a "virality score" based on:
- Hook strength (first 3 seconds)
- Retention signals (curiosity loops, reveals)
- Engagement potential (shareability, comment-bait)
- Trending format match

### Pricing
- Free tier available
- Pro tiers with more minutes/features
- API available for enterprise

### Results Claimed
- "Watch time increased by 57%"
- "Completion rate from 1-3% to 12+%"
- Used by: Grant Cardone, Logan Paul, Mark Rober

### What We Can Steal
1. **Virality scoring algorithm** — Our hypothesis scoring is similar
2. **ClipAnything approach** — Genre-agnostic analysis
3. **Reframe automation** — Subject tracking for vertical
4. **Completion rate optimization** — Focus on retention metrics

---

## 3. TubeBuddy (YouTube)

**Website:** https://tubebuddy.com  
**Focus:** YouTube SEO and analytics

### Key Features
- Keyword research
- A/B thumbnail testing
- Tag suggestions
- Competitor analysis
- Upload checklist

### Public API
- No public API
- Chrome extension based
- Data scraped from YouTube Studio

### Technical Approach
- Browser extension injects into YouTube
- Pulls data from YouTube Analytics API
- Compares against database of "what works"

### What We Can Learn
1. **Keyword optimization** — Track trending tags/hashtags
2. **A/B testing framework** — Test thumbnails/hooks
3. **Competitor tracking** — Monitor other creators
4. **Checklist approach** — Pre-publish optimization

---

## 4. vidIQ (YouTube)

**Website:** https://vidiq.com  
**Focus:** YouTube growth and analytics

### Key Features
- Daily Ideas (AI-generated content ideas)
- SEO score for videos
- Competitor tracking
- Trending video alerts
- Thumbnail generator

### Technical Approach
- Browser extension + web app
- YouTube Data API integration
- ML models for trend prediction

### API
- Limited API for enterprise
- Most features via extension

### What We Can Learn
1. **Daily ideas generation** — AI content suggestions
2. **SEO scoring** — Rate videos before posting
3. **Trend alerts** — Real-time viral detection
4. **Predictive analytics** — Forecast video performance

---

## Summary: Features to Build

| Feature | Source | Priority |
|---------|--------|----------|
| Virality scoring | OpusClip | HIGH |
| Sentiment peak detection | Vidyo/Quso | HIGH |
| Hook analysis (first 3s) | OpusClip | HIGH |
| Curiosity loop detection | Our design | HIGH |
| Trending audio tracking | Original | HIGH |
| A/B testing framework | TubeBuddy | MEDIUM |
| Daily ideas generation | vidIQ | MEDIUM |
| Reframe automation | OpusClip | LOW |
| SEO scoring | vidIQ | LOW |

---

## Technical Architecture Comparison

```
OpusClip Architecture (Inferred):
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Video Input │────▶│ Transcript  │────▶│ NLP Analysis│
└─────────────┘     │ (Whisper?)  │     │ (GPT-based?)│
                    └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────┐           │
                    │ Computer    │◀──────────┘
                    │ Vision      │
                    │ (Object     │
                    │  Tracking)  │
                    └─────────────┘
                           │
                    ┌─────────────┐     ┌─────────────┐
                    │ Virality    │────▶│ Clip        │
                    │ Scorer      │     │ Generator   │
                    └─────────────┘     └─────────────┘

Our ContentRadar Architecture:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Apify       │────▶│ yt-dlp      │────▶│ ffmpeg      │
│ (metadata)  │     │ (download)  │     │ (frames/    │
└─────────────┘     └─────────────┘     │  audio)     │
                                        └─────────────┘
                                              │
                    ┌─────────────┐           │
                    │ Groq        │◀──────────┤
                    │ Whisper     │           │
                    │ (lang=en)   │           │
                    └─────────────┘           │
                           │                  │
                    ┌─────────────┐     ┌─────────────┐
                    │ Claude      │     │ Gemini      │
                    │ (content)   │     │ (vision)    │
                    └─────────────┘     └─────────────┘
                           │                  │
                    ┌─────────────┘───────────┘
                    │
                    ▼
            ┌─────────────┐     ┌─────────────┐
            │ Hypothesis  │────▶│ Swipe Files │
            │ Scoring     │     │ + Alerts    │
            └─────────────┘     └─────────────┘
```

---

## Conclusion

**Key insight:** OpusClip's "virality scoring" is the closest to what we're building with hypothesis scoring. The main difference is:

- **OpusClip:** Predicts which CLIPS from a long video will go viral
- **ContentRadar:** Analyzes EXISTING viral content to understand WHY + build templates

We're more focused on **reverse-engineering success** rather than **predicting it upfront**.

**Recommendation:** Our approach is complementary — we can add a "pre-publish scoring" feature later that uses our hypothesis weights to predict performance BEFORE posting.
