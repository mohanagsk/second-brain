"""
analyze.py - Content analysis with Claude and Gemini
"""
import os
import base64
from typing import List, Optional, Dict, Any
from pathlib import Path
import anthropic
import google.generativeai as genai


class ContentAnalyzer:
    """Analyze content with Claude Sonnet and Gemini"""
    
    def __init__(self, claude_api_key: Optional[str] = None, 
                 gemini_api_key: Optional[str] = None):
        """
        Initialize analyzers
        
        Args:
            claude_api_key: Anthropic API key (or reads from ANTHROPIC_API_KEY)
            gemini_api_key: Google Gemini API key (or reads from GEMINI_API_KEY)
        """
        # Claude setup
        self.claude_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.claude_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        self.claude = anthropic.Anthropic(api_key=self.claude_key)
        self.claude_model = "claude-sonnet-4-20250514"
        
        # Gemini setup
        self.gemini_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not found")
        genai.configure(api_key=self.gemini_key)
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    def analyze_content_claude(self, post_data: dict, transcription: str) -> dict:
        """
        Analyze post content and transcription with Claude
        
        Args:
            post_data: Instagram post metadata (caption, likes, comments, etc.)
            transcription: Audio transcription text
            
        Returns:
            Dictionary with analysis results
        """
        prompt = f"""Analyze this Instagram Reel/post for content strategy insights:

POST METADATA:
- Username: {post_data.get('username', 'Unknown')}
- Caption: {post_data.get('caption', 'No caption')}
- Likes: {post_data.get('likes', 0):,}
- Comments: {post_data.get('comments', 0):,}
- Views: {post_data.get('views', 0):,}
- Posted: {post_data.get('timestamp', 'Unknown')}

TRANSCRIPTION:
{transcription}

Provide a structured analysis:

1. HOOK ANALYSIS
   - What hook technique is used in first 3 seconds?
   - Hook effectiveness score (1-10)

2. CONTENT BREAKDOWN
   - Main topic/theme
   - Key talking points
   - Content structure (story arc, list, tutorial, etc.)

3. ENGAGEMENT DRIVERS
   - What makes this content engaging?
   - Emotional triggers used
   - Call-to-action effectiveness

4. COPYWRITING PATTERNS
   - Caption strategy
   - Key phrases that drive engagement
   - Hashtag strategy (if visible)

5. VIRALITY FACTORS
   - Why is this performing above average?
   - Audience resonance points
   - Shareability score (1-10)

6. SWIPEABLE INSIGHTS
   - Top 3 tactics to replicate
   - Content formula (template)
   - Recommended use cases

Be specific and actionable. Focus on patterns that can be replicated."""

        try:
            response = self.claude.messages.create(
                model=self.claude_model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return {
                "analysis": response.content[0].text,
                "model": self.claude_model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_visuals_gemini(self, frame_paths: List[str], post_data: dict) -> dict:
        """
        Analyze video frames with Gemini vision
        
        Args:
            frame_paths: List of paths to extracted video frames
            post_data: Post metadata for context
            
        Returns:
            Dictionary with visual analysis results
        """
        if not frame_paths:
            return {"error": "No frames provided"}
        
        # Load and prepare images
        images = []
        for frame_path in frame_paths:
            if Path(frame_path).exists():
                images.append(genai.upload_file(frame_path))
        
        if not images:
            return {"error": "No valid frames found"}
        
        prompt = f"""Analyze these video frames from a high-performing Instagram Reel:

POST CONTEXT:
- Likes: {post_data.get('likes', 0):,}
- Comments: {post_data.get('comments', 0):,}
- Views: {post_data.get('views', 0):,}

Provide a detailed visual analysis:

1. VISUAL STYLE
   - Lighting and color grading
   - Shot composition and framing
   - Camera movement/transitions
   - Overall aesthetic

2. ON-SCREEN ELEMENTS
   - Text overlays (style, timing, content)
   - Graphics or animations
   - B-roll or cutaways
   - Face/person presence and expression

3. PRODUCTION QUALITY
   - Professional vs raw/authentic feel
   - Equipment quality indicators
   - Editing sophistication
   - Audio-visual sync quality

4. ENGAGEMENT OPTIMIZATION
   - Visual hooks in first frame
   - Pattern interrupts throughout
   - Visual pacing and rhythm
   - Thumbnail potential

5. VISUAL STORYTELLING
   - How visuals support the narrative
   - Scene progression and flow
   - Emotional journey through visuals

6. REPLICABLE TECHNIQUES
   - Camera angles to copy
   - Editing patterns to use
   - Visual effects worth trying
   - Equipment needed (estimate)

Be specific about what makes the visuals work. Focus on actionable insights."""

        try:
            response = self.gemini_model.generate_content([prompt] + images)
            
            return {
                "analysis": response.text,
                "model": "gemini-2.0-flash-exp",
                "frame_count": len(images)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def generate_swipe_file_entry(self, post_data: dict, claude_analysis: dict, 
                                  gemini_analysis: dict, transcription: str) -> str:
        """
        Generate formatted swipe file entry
        
        Args:
            post_data: Post metadata
            claude_analysis: Content analysis from Claude
            gemini_analysis: Visual analysis from Gemini
            transcription: Audio transcription
            
        Returns:
            Markdown-formatted swipe file entry
        """
        engagement_rate = 0
        if post_data.get('followers', 0) > 0:
            engagement_rate = (post_data.get('likes', 0) / post_data.get('followers', 1)) * 100
        
        entry = f"""---
# @{post_data.get('username', 'Unknown')} - {post_data.get('timestamp', 'Unknown')}

**Post URL:** {post_data.get('url', 'N/A')}
**Performance:** {post_data.get('likes', 0):,} likes | {post_data.get('comments', 0):,} comments | {post_data.get('views', 0):,} views
**Engagement Rate:** {engagement_rate:.2f}%
**Outlier Factor:** {post_data.get('outlier_factor', 0):.1f}x average

---

## 📝 CAPTION
{post_data.get('caption', 'No caption')}

---

## 🎙️ TRANSCRIPTION
{transcription}

---

## 🧠 CONTENT ANALYSIS (Claude)
{claude_analysis.get('analysis', 'Analysis failed')}

---

## 🎨 VISUAL ANALYSIS (Gemini)
{gemini_analysis.get('analysis', 'Analysis failed')}

---

## 💡 QUICK TAKEAWAYS
- **Hook:** {post_data.get('hook_summary', 'N/A')}
- **Format:** {post_data.get('format', 'N/A')}
- **Best for:** {post_data.get('best_use_case', 'N/A')}

---
"""
        return entry


if __name__ == "__main__":
    # Test the analyzer
    analyzer = ContentAnalyzer()
    print("ContentAnalyzer initialized successfully")
    print(f"Claude model: {analyzer.claude_model}")
    print(f"Gemini model: gemini-2.0-flash-exp")
