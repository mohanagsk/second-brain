#!/usr/bin/env python3
"""
Romanization Testing Script
Tests different methods to convert Hindi audio to romanized (English letter) transcripts
"""

import os
import json
import time
from pathlib import Path
import subprocess

# Configuration
AUDIO_DIR = Path("/home/divykairoth/.openclaw/workspace/instagram-intel/tests/audio_samples")
RESULTS_FILE = Path("/home/divykairoth/.openclaw/workspace/instagram-intel/tests/romanization_results.json")

AUDIO_FILES = [
    "audio_1.mp3",
    "audio_2.mp3", 
    "audio_3.mp3",
    "audio_4.mp3",
    "audio_5.mp3"
]

results = {}

# Method 1: Groq Whisper with language=en (force English output)
def test_groq_whisper_en(audio_file):
    """Test Groq Whisper API with language forced to English"""
    try:
        from openai import OpenAI
        
        # Groq uses OpenAI-compatible API
        client = OpenAI(
            api_key=os.environ.get("GROQ_API_KEY", ""),
            base_url="https://api.groq.com/openai/v1"
        )
        
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="en",  # Force English output
                response_format="text"
            )
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "transcript": transcription,
            "time": elapsed,
            "cost": 0.00001 * (os.path.getsize(audio_file) / 1024 / 1024),  # Estimate
            "notes": "Forced language=en parameter"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "notes": "Groq API key may not be configured"
        }

# Method 2: Groq Whisper + transliteration library
def test_groq_whisper_transliterate(audio_file):
    """Test Groq Whisper (default Hindi) + transliteration"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.environ.get("GROQ_API_KEY", ""),
            base_url="https://api.groq.com/openai/v1"
        )
        
        start_time = time.time()
        
        # First get Hindi transcript
        with open(audio_file, "rb") as f:
            hindi_text = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="hi",  # Hindi
                response_format="text"
            )
        
        # Try to transliterate using indic-transliteration
        try:
            from indic_transliteration import sanscript
            from indic_transliteration.sanscript import transliterate
            
            romanized = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS)
            
        except ImportError:
            # Fallback: simple character mapping
            romanized = transliterate_simple(hindi_text)
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "transcript_hindi": hindi_text,
            "transcript_roman": romanized,
            "time": elapsed,
            "cost": 0.00001 * (os.path.getsize(audio_file) / 1024 / 1024),
            "notes": "Two-step: Whisper(hi) + transliteration"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def transliterate_simple(text):
    """Simple Devanagari to Roman transliteration mapping"""
    # This is a basic mapping - real library would be much better
    mapping = {
        'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha',
        'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha',
        'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha',
        'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha',
        'न': 'na', 'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha',
        'म': 'ma', 'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
        'श': 'sha', 'ष': 'sha', 'स': 'sa', 'ह': 'ha',
        'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
        'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
        'ं': 'm', 'ः': 'h', '्': '',
        ' ': ' ', '।': '.', '?': '?', '!': '!',
    }
    
    result = []
    for char in text:
        result.append(mapping.get(char, char))
    return ''.join(result)

# Method 3: Google Cloud Speech-to-Text (native romanization)
def test_google_speech_to_text(audio_file):
    """Test Google Cloud Speech-to-Text with native romanization"""
    try:
        from google.cloud import speech
        
        # Note: Requires GOOGLE_APPLICATION_CREDENTIALS env var
        client = speech.SpeechClient()
        
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            content = f.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=44100,
            language_code="hi-IN",
            enable_automatic_punctuation=True,
            # Google supports romanization in some languages
            alternative_language_codes=["en-US"]
        )
        
        response = client.recognize(config=config, audio=audio)
        
        transcript = " ".join([result.alternatives[0].transcript 
                              for result in response.results])
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "transcript": transcript,
            "time": elapsed,
            "cost": 0.006 * (os.path.getsize(audio_file) / 60 / 1024 / 1024),  # $0.006/min
            "notes": "Google Cloud Speech-to-Text"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "notes": "Requires GOOGLE_APPLICATION_CREDENTIALS"
        }

# Method 4: Post-process Devanagari → Roman with AI (Gemini)
def test_ai_transliteration(audio_file):
    """Get Hindi transcript then use AI to romanize"""
    try:
        from openai import OpenAI
        import google.generativeai as genai
        
        # Step 1: Get Hindi transcript from Whisper
        client = OpenAI(
            api_key=os.environ.get("GROQ_API_KEY", ""),
            base_url="https://api.groq.com/openai/v1"
        )
        
        with open(audio_file, "rb") as f:
            hindi_text = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="hi",
                response_format="text"
            )
        
        # Step 2: Use Gemini to romanize
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        start_time = time.time()
        
        prompt = f"""Convert this Hindi text to romanized form (English letters).
Keep the Hindi words but write them in English letters exactly as they sound.

Example:
Input: "क्या सीन है भाई"
Output: "kya scene hai bhai"

Hindi text: {hindi_text}

Romanized output:"""
        
        response = model.generate_content(prompt)
        romanized = response.text.strip()
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "transcript_hindi": hindi_text,
            "transcript_roman": romanized,
            "time": elapsed,
            "cost": 0.00002,  # Groq + Gemini estimate
            "notes": "Two-step: Whisper(hi) + Gemini romanization"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Method 5: OpenAI Whisper with romanize parameter (if exists)
def test_openai_whisper_romanize(audio_file):
    """Test if OpenAI Whisper has romanize option"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        
        start_time = time.time()
        
        # Try with language=en (similar to Groq test)
        with open(audio_file, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="en",
                response_format="text"
            )
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "transcript": transcription,
            "time": elapsed,
            "cost": 0.006 * (os.path.getsize(audio_file) / 60 / 1024 / 1024),
            "notes": "OpenAI Whisper with language=en"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "notes": "Requires OPENAI_API_KEY"
        }

# Main test runner
def main():
    print("🎯 Hindi Romanization Testing Framework\n")
    print("=" * 60)
    
    # Check for API keys
    print("\n📋 Checking API credentials...")
    has_groq = bool(os.environ.get("GROQ_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
    has_google_cloud = bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    
    print(f"  Groq API: {'✅' if has_groq else '❌'}")
    print(f"  OpenAI API: {'✅' if has_openai else '❌'}")
    print(f"  Gemini API: {'✅' if has_gemini else '❌'}")
    print(f"  Google Cloud: {'✅' if has_google_cloud else '❌'}")
    
    # Test each audio file with each method
    for audio_file in AUDIO_FILES:
        audio_path = AUDIO_DIR / audio_file
        if not audio_path.exists():
            continue
            
        print(f"\n\n{'='*60}")
        print(f"🎵 Testing: {audio_file}")
        print(f"   Size: {os.path.getsize(audio_path) / 1024:.1f} KB")
        print(f"{'='*60}")
        
        file_results = {}
        
        # Method 1: Groq Whisper EN
        if has_groq:
            print("\n1️⃣ Groq Whisper (language=en)...")
            result = test_groq_whisper_en(audio_path)
            file_results["groq_whisper_en"] = result
            if result["success"]:
                print(f"   ✅ Time: {result['time']:.2f}s")
                print(f"   📝 Transcript: {result['transcript'][:100]}...")
        
        # Method 2: Groq Whisper + Transliteration
        if has_groq:
            print("\n2️⃣ Groq Whisper + Transliteration...")
            result = test_groq_whisper_transliterate(audio_path)
            file_results["groq_transliterate"] = result
            if result["success"]:
                print(f"   ✅ Time: {result['time']:.2f}s")
                print(f"   📝 Roman: {result['transcript_roman'][:100]}...")
        
        # Method 3: Google Cloud Speech
        if has_google_cloud:
            print("\n3️⃣ Google Cloud Speech-to-Text...")
            result = test_google_speech_to_text(audio_path)
            file_results["google_speech"] = result
            if result["success"]:
                print(f"   ✅ Time: {result['time']:.2f}s")
                print(f"   📝 Transcript: {result['transcript'][:100]}...")
        
        # Method 4: AI Transliteration (Gemini)
        if has_groq and has_gemini:
            print("\n4️⃣ Whisper + AI Romanization (Gemini)...")
            result = test_ai_transliteration(audio_path)
            file_results["ai_romanize"] = result
            if result["success"]:
                print(f"   ✅ Time: {result['time']:.2f}s")
                print(f"   📝 Roman: {result['transcript_roman'][:100]}...")
        
        # Method 5: OpenAI Whisper
        if has_openai:
            print("\n5️⃣ OpenAI Whisper (language=en)...")
            result = test_openai_whisper_romanize(audio_path)
            file_results["openai_whisper"] = result
            if result["success"]:
                print(f"   ✅ Time: {result['time']:.2f}s")
                print(f"   📝 Transcript: {result['transcript'][:100]}...")
        
        results[audio_file] = file_results
        
        # Save intermediate results
        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n\n" + "="*60)
    print("✅ Testing complete!")
    print(f"📊 Results saved to: {RESULTS_FILE}")
    print("="*60)

if __name__ == "__main__":
    main()
