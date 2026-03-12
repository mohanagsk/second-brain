# Weighted Hypothesis Scoring — Design Document

**Purpose:** Score new videos against proven hypothesis parameters to predict virality

---

## Concept

Instead of just analyzing content, we:
1. Build hypotheses from proven outliers ("Question hooks work")
2. Assign weights based on validation data
3. Score NEW videos against these weighted parameters
4. Track which hypotheses predict best over time

---

## Hypothesis Structure

```python
@dataclass
class Hypothesis:
    id: str
    name: str
    description: str
    
    # Detection parameters
    detection_rules: List[str]  # How to detect this pattern
    
    # Validation data
    times_tested: int
    times_confirmed: int
    confidence: float  # confirmed / tested
    
    # Impact weight (how much this affects virality)
    weight: float  # 0.0 - 1.0
    
    # Examples
    positive_examples: List[str]  # Reels where this worked
    negative_examples: List[str]  # Reels where this didn't work
```

---

## Hypothesis Database

```yaml
# hypotheses.yaml

hypotheses:
  H001_question_hooks:
    name: "Question Hooks"
    description: "Reels starting with a question get 3x more engagement"
    detection_rules:
      - "starts_with_question_word"
      - "ends_first_sentence_with_?"
    times_tested: 25
    times_confirmed: 18
    confidence: 0.72
    weight: 0.85
    positive_examples:
      - "@divy.kairoth/DQ6spa1keXI"  # 3.09M views
      - "@jaykapoor/ABC123"
    negative_examples:
      - "@creator/XYZ789"
    
  H002_comment_cta_first_5s:
    name: "Early Comment CTA"
    description: "Comment CTA in first 5 seconds doubles comment rate"
    detection_rules:
      - "cta_within_5_seconds"
      - "contains_comment_keyword"
    times_tested: 15
    times_confirmed: 12
    confidence: 0.80
    weight: 0.90
    
  H003_number_in_hook:
    name: "Number Hook"
    description: "Specific numbers in hook increase curiosity"
    detection_rules:
      - "hook_contains_number"
      - "number_is_specific"  # "₹79,000" not "many"
    times_tested: 20
    times_confirmed: 14
    confidence: 0.70
    weight: 0.75
    
  H004_contrast_loop:
    name: "Contrast/Before-After"
    description: "Before/after or contrast hooks retain 40% longer"
    detection_rules:
      - "contains_contrast_words"
      - "visual_transformation"
    times_tested: 12
    times_confirmed: 9
    confidence: 0.75
    weight: 0.80
    
  H005_trending_audio:
    name: "Trending Audio"
    description: "Using top 10 trending audio increases reach 2x"
    detection_rules:
      - "audio_in_trending_list"
    times_tested: 30
    times_confirmed: 21
    confidence: 0.70
    weight: 0.65
```

---

## Scoring Algorithm

```python
def score_reel_against_hypotheses(reel_data: dict, transcript: str) -> dict:
    """
    Score a reel against all validated hypotheses.
    Returns weighted viral potential score.
    """
    hypotheses = load_hypotheses()
    
    results = {
        "reel_id": reel_data["id"],
        "hypothesis_matches": [],
        "total_score": 0,
        "max_possible_score": 0,
        "viral_prediction": "low"
    }
    
    for h in hypotheses:
        # Only use hypotheses with >60% confidence
        if h.confidence < 0.6:
            continue
            
        results["max_possible_score"] += h.weight
        
        # Check if reel matches this hypothesis
        match = check_hypothesis_match(reel_data, transcript, h.detection_rules)
        
        if match:
            weighted_score = h.weight * h.confidence
            results["hypothesis_matches"].append({
                "hypothesis": h.id,
                "name": h.name,
                "confidence": h.confidence,
                "weight": h.weight,
                "contribution": weighted_score
            })
            results["total_score"] += weighted_score
    
    # Normalize score to 0-10
    if results["max_possible_score"] > 0:
        normalized = (results["total_score"] / results["max_possible_score"]) * 10
    else:
        normalized = 5  # Default
    
    results["normalized_score"] = round(normalized, 1)
    
    # Viral prediction
    if normalized >= 8:
        results["viral_prediction"] = "high"
    elif normalized >= 6:
        results["viral_prediction"] = "medium"
    else:
        results["viral_prediction"] = "low"
    
    return results
```

---

## Example Output

```markdown
## Hypothesis Score: @divy.kairoth/NEW_REEL

**Normalized Score:** 7.8/10
**Viral Prediction:** MEDIUM-HIGH

### Matched Hypotheses:

| Hypothesis | Confidence | Weight | Contribution |
|------------|------------|--------|--------------|
| H001 Question Hook | 72% | 0.85 | 0.61 |
| H002 Early CTA | 80% | 0.90 | 0.72 |
| H003 Number in Hook | 70% | 0.75 | 0.53 |
| H005 Trending Audio | 70% | 0.65 | 0.46 |

### Missing High-Impact Hypotheses:
- H004 Contrast Loop (weight: 0.80) — Consider adding before/after element

### Recommendation:
This reel matches 4/5 high-confidence hypotheses. 
Expected performance: **5-8x channel average** based on similar patterns.

### Comparable Past Outliers:
- @divy/DQ6spa1keXI matched same pattern → 53x avg
- @jay/XYZ123 matched same pattern → 8x avg
```

---

## Hypothesis Evolution

When new data comes in:

```python
def update_hypothesis(hypothesis_id: str, reel_id: str, was_outlier: bool):
    """
    Update hypothesis confidence based on new evidence.
    """
    h = load_hypothesis(hypothesis_id)
    
    h.times_tested += 1
    if was_outlier:
        h.times_confirmed += 1
        h.positive_examples.append(reel_id)
    else:
        h.negative_examples.append(reel_id)
    
    # Recalculate confidence
    h.confidence = h.times_confirmed / h.times_tested
    
    # Adjust weight based on confidence trend
    if h.confidence > 0.8:
        h.weight = min(1.0, h.weight * 1.05)  # Increase weight
    elif h.confidence < 0.5:
        h.weight = max(0.1, h.weight * 0.9)   # Decrease weight
    
    save_hypothesis(h)
```

---

## Integration with Pipeline

```
New Reel Scraped
    ↓
Transcribe + Analyze
    ↓
score_reel_against_hypotheses()
    ↓
Store prediction
    ↓
After 3-4 days:
    ↓
Check actual performance
    ↓
update_hypothesis() for each matched hypothesis
    ↓
Hypothesis weights evolve over time
```

---

## Weekly Hypothesis Report

```markdown
# 📈 Hypothesis Performance — Week of March 3, 2026

## Rising Hypotheses (confidence increasing)
| Hypothesis | Last Week | This Week | Trend |
|------------|-----------|-----------|-------|
| H002 Early CTA | 75% | 80% | ⬆️ +5% |
| H001 Question Hook | 70% | 72% | ⬆️ +2% |

## Falling Hypotheses (need review)
| Hypothesis | Last Week | This Week | Trend |
|------------|-----------|-----------|-------|
| H005 Trending Audio | 75% | 70% | ⬇️ -5% |

## New Hypotheses to Test
- H006: "Duet format increases reach" — needs 10+ tests
- H007: "Posting 6-9 PM IST optimal" — needs 15+ tests

## Predictions Made This Week: 23
## Predictions Verified: 18
## Overall Accuracy: 72%
```
