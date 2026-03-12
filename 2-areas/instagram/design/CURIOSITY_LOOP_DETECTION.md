# Curiosity Loop Detection — Algorithm Design

**Purpose:** Detect and categorize curiosity loops in Instagram reels

---

## What is a Curiosity Loop?

A curiosity loop is a narrative technique that creates an "open loop" in the viewer's mind — a question or mystery that MUST be answered. The viewer keeps watching to close the loop.

---

## Types of Curiosity Loops

### 1. **Question Hook Loop**
- Opens with a question that demands an answer
- Example: "Kya tumhe pata hai ye website sirf ₹99 mein..."
- Detection: Starts with question word (kya, kaise, kyu, kyun, what, how, why)

### 2. **Contrast Loop**
- Shows before/after or problem/solution
- Example: "Pehle mere paas 0 followers the... ab 10K"
- Detection: Contrast words (pehle/ab, before/after, was/now)

### 3. **List Loop**
- Promises multiple items, reveals them sequentially
- Example: "Ye 5 apps tumhari life change kar denge"
- Detection: Number + "things/apps/tricks/ways"

### 4. **Story Loop**
- Opens a narrative that must be completed
- Example: "Jab maine ye kiya tab sab badal gaya"
- Detection: Past tense narrative opener (jab, when, ek din)

### 5. **Challenge Loop**
- Issues a challenge viewer wants to see resolved
- Example: "Bet you can't do this in 10 seconds"
- Detection: Challenge words (bet, try, challenge, dare)

### 6. **Secret/Reveal Loop**
- Promises hidden information
- Example: "Ye trick koi nahi batata"
- Detection: Secret words (secret, hidden, koi nahi batata, nobody knows)

### 7. **Stakes Loop**
- Creates consequences for not watching
- Example: "Agar ye nahi kiya toh paise doob jayenge"
- Detection: Consequence words (agar, nahi toh, otherwise, warna)

---

## Detection Algorithm

```python
CURIOSITY_PATTERNS = {
    "question_hook": {
        "hindi": ["kya", "kaise", "kyu", "kyun", "kaun", "kab", "kahan"],
        "english": ["what", "how", "why", "who", "when", "where", "?"],
        "weight": 0.9
    },
    "contrast": {
        "hindi": ["pehle", "ab", "tha", "hai", "se", "tak"],
        "english": ["before", "after", "was", "now", "from", "to"],
        "weight": 0.8
    },
    "list": {
        "patterns": [r"\d+\s*(things|apps|tricks|ways|tips|hacks)", 
                     r"\d+\s*(cheezein|tarike|apps)"],
        "weight": 0.85
    },
    "story": {
        "hindi": ["jab", "ek din", "ek baar", "mere saath"],
        "english": ["when i", "one day", "once", "story time"],
        "weight": 0.75
    },
    "challenge": {
        "hindi": ["try karo", "challenge", "dare"],
        "english": ["bet you", "try this", "challenge", "dare you"],
        "weight": 0.8
    },
    "secret": {
        "hindi": ["koi nahi batata", "secret", "hidden"],
        "english": ["nobody knows", "secret", "hidden", "they don't want"],
        "weight": 0.85
    },
    "stakes": {
        "hindi": ["agar", "nahi toh", "warna", "galti"],
        "english": ["if you don't", "otherwise", "or else", "mistake"],
        "weight": 0.7
    }
}

def detect_curiosity_loops(transcript: str, first_5_seconds: str) -> dict:
    """
    Analyze content for curiosity loops.
    Returns detected loops with confidence scores.
    """
    results = {
        "loops_detected": [],
        "primary_loop": None,
        "loop_score": 0,
        "retention_prediction": "low"
    }
    
    # Normalize text
    text = transcript.lower()
    hook = first_5_seconds.lower()
    
    for loop_type, patterns in CURIOSITY_PATTERNS.items():
        score = 0
        
        # Check hook (first 5 seconds) — weighted higher
        for pattern in patterns.get("hindi", []) + patterns.get("english", []):
            if pattern in hook:
                score += patterns["weight"] * 1.5  # Hook bonus
            elif pattern in text:
                score += patterns["weight"] * 0.5
        
        # Check regex patterns
        for regex in patterns.get("patterns", []):
            if re.search(regex, text, re.IGNORECASE):
                score += patterns["weight"]
        
        if score > 0.5:
            results["loops_detected"].append({
                "type": loop_type,
                "confidence": min(score, 1.0)
            })
    
    # Calculate overall loop score
    if results["loops_detected"]:
        results["loops_detected"].sort(key=lambda x: x["confidence"], reverse=True)
        results["primary_loop"] = results["loops_detected"][0]["type"]
        results["loop_score"] = sum(l["confidence"] for l in results["loops_detected"]) / len(results["loops_detected"])
        
        # Retention prediction based on loop strength
        if results["loop_score"] > 0.8:
            results["retention_prediction"] = "high"
        elif results["loop_score"] > 0.5:
            results["retention_prediction"] = "medium"
    
    return results
```

---

## Scoring Matrix

| Loop Type | Base Weight | In Hook Multiplier | Retention Impact |
|-----------|-------------|-------------------|------------------|
| Question Hook | 0.90 | 1.5x | Very High |
| Secret/Reveal | 0.85 | 1.5x | Very High |
| List | 0.85 | 1.3x | High |
| Contrast | 0.80 | 1.4x | High |
| Challenge | 0.80 | 1.3x | Medium-High |
| Story | 0.75 | 1.2x | Medium |
| Stakes | 0.70 | 1.4x | Medium |

---

## Output Format for Swipe File

```markdown
## Curiosity Loop Analysis

**Reel:** @creator/reel_id
**Primary Loop:** Question Hook (confidence: 0.92)
**Secondary Loops:** Secret (0.65), Stakes (0.55)
**Overall Loop Score:** 0.87/1.0
**Retention Prediction:** HIGH

### Loop Breakdown:
- **Hook (0-3s):** "Kya tumhe pata hai ye trick?" → Question loop opens
- **Build (3-15s):** Stakes established ("nahi kiya toh miss ho jayega")
- **Payoff (15-30s):** Answer revealed, loop closed
- **CTA (30s):** New loop opened ("comment karo for more")

### Replication Template:
"[Question word] [subject] [curiosity gap]?"
Example: "Kya tumhe pata hai ye [X] sirf [small number] mein mil sakta hai?"
```

---

## Integration with Analysis Pipeline

```
Transcript
    ↓
detect_curiosity_loops(transcript, first_5s)
    ↓
┌─────────────────────────────┐
│ Loop Analysis Results       │
│ - Primary loop type         │
│ - Confidence scores         │
│ - Retention prediction      │
│ - Replication template      │
└─────────────────────────────┘
    ↓
Swipe File Entry
```

---

## Future Enhancements

1. **ML-based detection** — Train on labeled dataset of viral vs non-viral
2. **Visual loop detection** — Detect visual cliffhangers (cut before reveal)
3. **Audio loop detection** — Music builds that create tension
4. **Multi-loop scoring** — Bonus for multiple overlapping loops
