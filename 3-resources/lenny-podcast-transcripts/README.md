# Lenny's Podcast Transcripts

**Downloaded:** March 12, 2026
**Total:** 299 transcripts (1 video had captions disabled)
**Size:** 59MB clean text

## Structure
- `transcripts/{video_id}.txt` — plain text transcript (no timestamps)
- `video_metadata.txt` — `video_id|title` mapping
- `target_300.txt` — list of 300 video IDs downloaded

## Quick Search
```bash
# Find all mentions of a topic
grep -l "product market fit" transcripts/*.txt

# Search with context
grep -r "retention" transcripts/ -C 2

# Count mentions across all episodes
grep -c "AI" transcripts/*.txt | sort -t: -k2 -nr | head -20
```

## Sample Videos
| Video ID | Title |
|----------|-------|
| HEqrvF7ztBE | How I built a 1M+ subscriber newsletter and top 10 tech podcast |
| eh8bcBIAAFo | The design process is dead. Here's what's replacing it. |
| We7BZVKbCVw | Head of Claude Code: What happens after coding is solved |
| 87Pm0SGTtN8 | Marc Andreessen: The real AI boom hasn't even started yet |

## Notes
- Downloaded using `youtube-transcript-api` Python library (free)
- 12 parallel threads, ~60 seconds total
- Only 1 video (`s0jn7eE33nk`) had transcripts disabled
