# A/B Model Tracking — Design Document

**Purpose:** Track AI model performance over time to identify which models predict virality best

---

## Why Track Models?

Divy wants to test different models and see which ones give better analysis over time. This creates a feedback loop:

```
Model predicts "this will go viral"
    ↓
Content is created/analyzed
    ↓
Actual performance measured
    ↓
Model accuracy scored
    ↓
Best models identified for each task
```

---

## Tracking Schema

```python
@dataclass
class ModelPrediction:
    prediction_id: str
    timestamp: datetime
    model: str  # "claude-sonnet", "claude-opus", "gemini-pro"
    task: str   # "hook_analysis", "retention", "cta", "overall_viral"
    reel_id: str
    
    # Predictions (1-10 scale)
    predicted_hook_score: float
    predicted_retention_score: float
    predicted_cta_score: float
    predicted_viral_score: float
    
    # Actual outcomes (filled later)
    actual_views: Optional[int] = None
    actual_outlier_score: Optional[float] = None
    actual_engagement_rate: Optional[float] = None
    
    # Accuracy (calculated after outcomes known)
    prediction_accuracy: Optional[float] = None

@dataclass
class ModelPerformance:
    model: str
    task: str
    total_predictions: int
    avg_accuracy: float
    best_at: List[str]  # What this model excels at
    worst_at: List[str]  # Where it struggles
```

---

## Tracking Database

```yaml
# model_tracking.yaml

models:
  claude-sonnet:
    predictions: 45
    accuracy:
      hook_analysis: 0.78
      retention: 0.72
      cta: 0.81
      overall_viral: 0.75
    best_at: ["cta", "hook_analysis"]
    cost_per_analysis: 0.01
    
  claude-opus:
    predictions: 12
    accuracy:
      hook_analysis: 0.85
      retention: 0.82
      cta: 0.79
      overall_viral: 0.83
    best_at: ["retention", "overall_viral"]
    cost_per_analysis: 0.07
    
  gemini-pro:
    predictions: 30
    accuracy:
      hook_analysis: 0.71
      retention: 0.68
      cta: 0.74
      overall_viral: 0.70
    best_at: ["visual_analysis"]
    cost_per_analysis: 0.00

predictions:
  - id: "pred_001"
    model: "claude-sonnet"
    reel: "@divy.kairoth/ABC123"
    predicted_viral: 7.5
    actual_outlier_score: 3.2
    accuracy: 0.65
    timestamp: "2026-03-03T10:00:00Z"
```

---

## Accuracy Calculation

```python
def calculate_accuracy(predicted_viral: float, actual_outlier_score: float) -> float:
    """
    Calculate prediction accuracy.
    
    predicted_viral: 1-10 scale
    actual_outlier_score: views / avg (e.g., 3.5x = 3.5)
    
    Returns: 0-1 accuracy score
    """
    # Normalize outlier score to 1-10 scale
    # 1x = 1, 3x = 5, 5x = 7, 10x+ = 10
    if actual_outlier_score >= 10:
        actual_normalized = 10
    elif actual_outlier_score >= 5:
        actual_normalized = 7 + (actual_outlier_score - 5) * 0.6
    elif actual_outlier_score >= 3:
        actual_normalized = 5 + (actual_outlier_score - 3) * 1.0
    else:
        actual_normalized = 1 + (actual_outlier_score - 1) * 2.0
    
    # Calculate accuracy (inverse of error)
    error = abs(predicted_viral - actual_normalized)
    accuracy = max(0, 1 - (error / 10))
    
    return accuracy
```

---

## Weekly Model Report

```markdown
# 📊 Model Performance Report — Week of March 3, 2026

## Overall Rankings

| Rank | Model | Predictions | Avg Accuracy | Best Task |
|------|-------|-------------|--------------|-----------|
| 1 | Claude Opus | 12 | 83% | Overall Viral |
| 2 | Claude Sonnet | 45 | 75% | CTA Analysis |
| 3 | Gemini Pro | 30 | 70% | Visual Analysis |

## Task-Specific Winners

| Task | Best Model | Accuracy | Runner-up |
|------|-----------|----------|-----------|
| Hook Analysis | Opus (85%) | ✅ | Sonnet (78%) |
| Retention | Opus (82%) | ✅ | Sonnet (72%) |
| CTA | Sonnet (81%) | ✅ | Opus (79%) |
| Visual | Gemini (76%) | ✅ | Sonnet (68%) |
| Overall Viral | Opus (83%) | ✅ | Sonnet (75%) |

## Cost-Effectiveness

| Model | Accuracy | Cost/Analysis | Value Score |
|-------|----------|---------------|-------------|
| Claude Sonnet | 75% | $0.01 | ⭐⭐⭐⭐⭐ |
| Gemini Pro | 70% | $0.00 | ⭐⭐⭐⭐ |
| Claude Opus | 83% | $0.07 | ⭐⭐⭐ |

## Recommendation

**Daily Analysis:** Claude Sonnet (best value)
**Weekly Deep Dive:** Claude Opus (highest accuracy)
**Visual Analysis:** Gemini Pro (free + good quality)

## Predictions to Verify This Week

| Reel | Model | Predicted | Check After |
|------|-------|-----------|-------------|
| @divy/XYZ | Sonnet | 8.2 | Mar 6 |
| @jay/ABC | Opus | 7.5 | Mar 6 |
```

---

## Integration with Pipeline

```
New Reel Analyzed
    ↓
Store prediction with model name
    ↓
After 3-4 days (half-life):
    ↓
Fetch actual performance
    ↓
Calculate accuracy
    ↓
Update model_tracking.yaml
    ↓
Weekly: Generate model report
```

---

## Future: Auto-Select Best Model

```python
def select_best_model(task: str, budget: str = "normal") -> str:
    """
    Auto-select best model based on historical performance.
    
    budget: "low" (free only), "normal" (up to $0.01), "high" (any)
    """
    models = load_model_performance()
    
    if budget == "low":
        candidates = [m for m in models if m.cost <= 0]
    elif budget == "normal":
        candidates = [m for m in models if m.cost <= 0.01]
    else:
        candidates = models
    
    # Sort by accuracy for this task
    candidates.sort(key=lambda m: m.accuracy[task], reverse=True)
    
    return candidates[0].name
```
