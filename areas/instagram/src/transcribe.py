"""
transcribe.py - Groq Whisper transcription
"""
import os
from pathlib import Path
from typing import Optional
import requests


class Transcriber:
    """Handle audio transcription with Groq Whisper API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize transcriber
        
        Args:
            api_key: Groq API key (or reads from GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment or parameters")
        
        self.api_url = "https://api.groq.com/openai/v1/audio/transcriptions"
        self.model = "whisper-large-v3"
    
    def transcribe(self, audio_path: str, language: str = "en") -> dict:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file (mp3, mp4, wav, etc.)
            language: Language code (default: 'en' for English/romanized)
            
        Returns:
            Dictionary with transcription results:
            {
                "text": "full transcription",
                "language": "detected_language",
                "duration": seconds
            }
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Prepare the request
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        with open(audio_path, "rb") as audio_file:
            files = {
                "file": (audio_path.name, audio_file, "audio/mpeg")
            }
            data = {
                "model": self.model,
                "language": language,
                "response_format": "verbose_json"
            }
            
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout for long files
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "text": result.get("text", ""),
                    "language": result.get("language", language),
                    "duration": result.get("duration", 0),
                    "segments": result.get("segments", [])
                }
                
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Transcription API request failed: {e}")
            except ValueError as e:
                raise RuntimeError(f"Failed to parse API response: {e}")
    
    def transcribe_batch(self, audio_paths: list, language: str = "en") -> dict:
        """
        Transcribe multiple audio files
        
        Args:
            audio_paths: List of paths to audio files
            language: Language code
            
        Returns:
            Dictionary mapping file paths to transcription results
        """
        results = {}
        for audio_path in audio_paths:
            try:
                results[audio_path] = self.transcribe(audio_path, language)
            except Exception as e:
                print(f"Error transcribing {audio_path}: {e}")
                results[audio_path] = {"error": str(e)}
        
        return results


if __name__ == "__main__":
    # Test the transcriber
    import sys
    
    if len(sys.argv) > 1:
        transcriber = Transcriber()
        result = transcriber.transcribe(sys.argv[1])
        print(f"Transcription: {result['text']}")
        print(f"Language: {result['language']}")
        print(f"Duration: {result['duration']}s")
    else:
        print("Usage: python transcribe.py <audio_file>")
