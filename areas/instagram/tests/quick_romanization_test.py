#!/usr/bin/env python3
"""
Quick Romanization Test - Using available APIs
"""

import os
import json
import time
from pathlib import Path
from openai import OpenAI
import google.generativeai as genai

# Configuration
AUDIO_DIR = Path("/home/divykairoth/.openclaw/workspace/instagram-intel/tests/audio_samples")
OUTPUT_FILE = Path("/home/divykairoth/.openclaw/workspace/instagram-intel/tests/romanization_results.json")

AUDIO_FILES = ["audio_1.mp3", "audio_2.mp3", "audio_3.mp3", "audio_4.mp3", "audio_5.mp3"]

# Setup APIs
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDXilC6mjyqY_Hs-NMo_eS9DWZtfhPNVtQ")

groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

results = {}

def test_method_1_groq_en(audio_path, audio_name):
    """Method 1: Groq Whisper with language=en (force romanization)"""
    print(f"\n  Testing Method 1: Groq Whisper (language=en)...")
    try:
        start = time.time()
        with open(audio_path, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="en",
                response_format="text"
            )
        elapsed = time.time() - start
        
        return {
            "method": "Groq Whisper (language=en)",
            "success": True,
            "transcript": transcription,
            "time_seconds": round(elapsed, 2),
            "estimated_cost_usd": 0.00001 * (os.path.getsize(audio_path) / 1024 / 1024),
            "complexity": "Low - Single API call",
            "notes": "Forces Whisper to output in English letters"
        }
    except Exception as e:
        return {"method": "Groq Whisper (language=en)", "success": False, "error": str(e)}

def test_method_2_groq_hi_then_ai(audio_path, audio_name):
    """Method 2: Groq Whisper (Hindi) + Gemini romanization"""
    print(f"\n  Testing Method 2: Groq (Hindi) + Gemini Romanization...")
    try:
        # Step 1: Get Hindi transcript
        start = time.time()
        with open(audio_path, "rb") as f:
            hindi_text = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="hi",
                response_format="text"
            )
        
        # Step 2: Romanize with Gemini
        prompt = f"""Convert this Hindi text to romanized form using English letters.
Write Hindi words exactly as they sound when spoken.

Example:
Input: "क्या सीन है भाई"
Output: "kya scene hai bhai"

Hindi text: {hindi_text}

Romanized (English letters only):"""
        
        response = gemini_model.generate_content(prompt)
        romanized = response.text.strip()
        
        elapsed = time.time() - start
        
        return {
            "method": "Groq Hindi + Gemini Romanize",
            "success": True,
            "transcript_hindi": hindi_text,
            "transcript_roman": romanized,
            "time_seconds": round(elapsed, 2),
            "estimated_cost_usd": 0.00003,  # Groq + Gemini
            "complexity": "Medium - Two API calls",
            "notes": "Two-step: accurate Hindi → AI-powered romanization"
        }
    except Exception as e:
        return {"method": "Groq Hindi + Gemini Romanize", "success": False, "error": str(e)}

def test_method_3_groq_hi_simple(audio_path, audio_name):
    """Method 3: Groq Whisper (Hindi) with simple char mapping"""
    print(f"\n  Testing Method 3: Groq (Hindi) + Simple Mapping...")
    try:
        start = time.time()
        with open(audio_path, "rb") as f:
            hindi_text = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="hi",
                response_format="text"
            )
        
        # Simple character-by-character mapping
        mapping = {
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
            'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
            'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
            'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
            'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
            'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 'श': 'sha',
            'ष': 'sha', 'स': 'sa', 'ह': 'ha', 'क्ष': 'ksha', 'त्र': 'tra',
            'ज्ञ': 'gya', 'श्र': 'shra',
            'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
            'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'm', 'ः': 'h',
            '्': '', 'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u',
            'ऊ': 'oo', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            ' ': ' ', '।': '.', ',': ',', '?': '?', '!': '!', '\n': '\n'
        }
        
        result = []
        for char in hindi_text:
            result.append(mapping.get(char, char))
        romanized = ''.join(result)
        
        elapsed = time.time() - start
        
        return {
            "method": "Groq Hindi + Simple Char Mapping",
            "success": True,
            "transcript_hindi": hindi_text,
            "transcript_roman": romanized,
            "time_seconds": round(elapsed, 2),
            "estimated_cost_usd": 0.00001,
            "complexity": "Low - Single API call + simple logic",
            "notes": "Basic character mapping - may not handle context well"
        }
    except Exception as e:
        return {"method": "Groq Hindi + Simple Mapping", "success": False, "error": str(e)}

def evaluate_transcript(transcript):
    """Simple evaluation of romanization quality"""
    # Check for Devanagari characters (should be none in romanized)
    has_devanagari = any('\u0900' <= char <= '\u097F' for char in str(transcript))
    
    # Check for English letters
    has_english = any(char.isalpha() and char.isascii() for char in str(transcript))
    
    # Rough readability score
    if not has_devanagari and has_english:
        return "✅ Good - Pure romanized text"
    elif has_devanagari and has_english:
        return "⚠️  Mixed - Has both Devanagari and Roman"
    elif has_devanagari:
        return "❌ Failed - Still in Devanagari"
    else:
        return "⚠️  Unknown"

def main():
    print("="*70)
    print("🎯 HINDI ROMANIZATION TEST")
    print("="*70)
    print(f"\n📁 Audio Directory: {AUDIO_DIR}")
    print(f"🎵 Testing {len(AUDIO_FILES)} audio files")
    print(f"\n🔑 API Keys:")
    print(f"   Groq: {'✅' if GROQ_API_KEY else '❌'}")
    print(f"   Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    
    all_results = {}
    
    for i, audio_file in enumerate(AUDIO_FILES, 1):
        audio_path = AUDIO_DIR / audio_file
        if not audio_path.exists():
            print(f"\n⚠️  Skipping {audio_file} - file not found")
            continue
        
        print(f"\n{'='*70}")
        print(f"🎵 Audio {i}/{len(AUDIO_FILES)}: {audio_file}")
        print(f"   Size: {os.path.getsize(audio_path) / 1024:.1f} KB")
        print(f"{'='*70}")
        
        file_results = {}
        
        # Test Method 1: Groq with language=en
        result1 = test_method_1_groq_en(audio_path, audio_file)
        file_results["method_1_groq_en"] = result1
        if result1["success"]:
            print(f"  ✅ Method 1 completed in {result1['time_seconds']}s")
            print(f"     Quality: {evaluate_transcript(result1['transcript'])}")
            print(f"     Preview: {result1['transcript'][:80]}...")
        else:
            print(f"  ❌ Method 1 failed: {result1.get('error', 'Unknown error')}")
        
        # Test Method 2: Groq Hindi + Gemini
        result2 = test_method_2_groq_hi_then_ai(audio_path, audio_file)
        file_results["method_2_groq_gemini"] = result2
        if result2["success"]:
            print(f"  ✅ Method 2 completed in {result2['time_seconds']}s")
            print(f"     Quality: {evaluate_transcript(result2['transcript_roman'])}")
            print(f"     Hindi: {result2['transcript_hindi'][:60]}...")
            print(f"     Roman: {result2['transcript_roman'][:60]}...")
        else:
            print(f"  ❌ Method 2 failed: {result2.get('error', 'Unknown error')}")
        
        # Test Method 3: Groq Hindi + Simple Mapping
        result3 = test_method_3_groq_hi_simple(audio_path, audio_file)
        file_results["method_3_simple_map"] = result3
        if result3["success"]:
            print(f"  ✅ Method 3 completed in {result3['time_seconds']}s")
            print(f"     Quality: {evaluate_transcript(result3['transcript_roman'])}")
            print(f"     Roman: {result3['transcript_roman'][:60]}...")
        else:
            print(f"  ❌ Method 3 failed: {result3.get('error', 'Unknown error')}")
        
        all_results[audio_file] = file_results
        
        # Brief pause between files
        time.sleep(1)
    
    # Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n{'='*70}")
    print(f"✅ Testing Complete!")
    print(f"📊 Results saved to: {OUTPUT_FILE}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
