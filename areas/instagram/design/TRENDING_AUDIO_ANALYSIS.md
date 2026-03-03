# Trending Audio Analysis — Design Document

**Purpose:** Track and analyze trending audio/music in Instagram Reels

---

## Why Audio Matters

Trending audio is THE #1 factor for reel virality on Instagram. The algorithm heavily promotes content using trending sounds.

---

## Data Available from Apify

```json
{
  "musicInfo": {
    "musicId": "123456789",
    "musicName": "Original Audio",
    "artistName": "@creator",
    "musicUrl": "https://..."
  }
}
```

---

## Analysis Dimensions

### 1. Audio Popularity Tracking
- Count how many outliers use the same audio
- Track audio across multiple creators
- Identify audio trend curves (rising, peaking, falling)

### 2. Audio-Content Fit Analysis
- Does upbeat music work for tech content?
- Does emotional music work for story content?
- Match audio mood to content type

### 3. Original vs Trending Audio
- Original audio = creator's voice/music
- Trending audio = reused viral sound
- Which performs better for which content type?

### 4. Audio Timing
- When did creator jump on trend?
- Early adopters vs late followers
- Optimal window for trend adoption

---

## Implementation

```python
class AudioAnalyzer:
    def __init__(self):
        self.audio_db = {}  # Track audio across all scraped reels
    
    def track_audio(self, reel_data: dict):
        """Add audio to tracking database"""
        audio = reel_data.get("musicInfo", {})
        audio_id = audio.get("musicId")
        
        if audio_id:
            if audio_id not in self.audio_db:
                self.audio_db[audio_id] = {
                    "name": audio.get("musicName"),
                    "artist": audio.get("artistName"),
                    "first_seen": reel_data["timestamp"],
                    "usage_count": 0,
                    "outlier_count": 0,
                    "total_views": 0,
                    "creators": set()
                }
            
            self.audio_db[audio_id]["usage_count"] += 1
            self.audio_db[audio_id]["total_views"] += reel_data["plays"]
            self.audio_db[audio_id]["creators"].add(reel_data["username"])
            
            if reel_data.get("is_outlier"):
                self.audio_db[audio_id]["outlier_count"] += 1
    
    def get_trending_audio(self, min_outliers: int = 2) -> list:
        """Get audio that appears in multiple outliers"""
        trending = []
        for audio_id, data in self.audio_db.items():
            if data["outlier_count"] >= min_outliers:
                data["audio_id"] = audio_id
                data["outlier_rate"] = data["outlier_count"] / data["usage_count"]
                trending.append(data)
        
        return sorted(trending, key=lambda x: x["outlier_count"], reverse=True)
    
    def analyze_audio_fit(self, audio_id: str, content_type: str) -> dict:
        """Analyze if audio fits content type"""
        # This would use AI to analyze audio mood vs content
        pass
```

---

## Output: Trending Audio Report

```markdown
# 🎵 Trending Audio Report — Week of March 3, 2026

## Top Performing Audio This Week

| Rank | Audio Name | Artist | Outliers | Avg Views | Trend |
|------|-----------|--------|----------|-----------|-------|
| 1 | "Obsessed" | Riri | 5 | 1.2M | 🔥 Rising |
| 2 | "Original Audio" | @jaykapoor | 3 | 800K | ➡️ Stable |
| 3 | "Tum Hi Ho" | Arijit | 3 | 650K | ⬇️ Falling |

## Audio Trend Curves

### Rising (Jump on these NOW)
- "Obsessed" by Riri — 5 outliers in 3 days
- "New Sound X" — just started trending

### Peaking (Last chance)
- "Viral Sound Y" — saturating, 2-3 days left

### Falling (Too late)
- "Old Trend Z" — oversaturated

## Recommendations for @divy.kairoth

Based on your content style (tech/life hacks):
1. **Best fit:** "Obsessed" — energetic, works for reveals
2. **Good fit:** "Original Audio" — tech explanations
3. **Avoid:** "Tum Hi Ho" — too emotional for tech content
```

---

## Integration with Pipeline

```
Scrape Reels (Apify)
    ↓
Extract musicInfo
    ↓
AudioAnalyzer.track_audio()
    ↓
After all reels scraped:
    ↓
AudioAnalyzer.get_trending_audio()
    ↓
Generate weekly audio report
    ↓
Add to swipe files: swipe-files/audio/trending-this-week.md
```

---

## Swipe File Entry Format

```markdown
## 🎵 Audio: "Obsessed" by Riri

**Status:** 🔥 TRENDING (use within 3 days)
**Outlier Rate:** 45% (5/11 reels using this are outliers)
**Best For:** Reveals, transformations, before/after
**Avg Views:** 1.2M

**Creators Using It:**
- @jaykapoor.24 — 2.1M views
- @vedikabhaia — 1.8M views
- @techcreator — 900K views

**How They Used It:**
- Drop on beat = reveal moment
- 15-second version works best
- Pair with text overlay for impact
```
