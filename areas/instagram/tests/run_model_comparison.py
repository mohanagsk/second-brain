#!/usr/bin/env python3
"""
Multi-model Instagram Reel Analysis Comparison
Runs the same analysis prompt across Claude Opus, Sonnet, Gemini Pro, and GPT-4
"""

import anthropic
import google.generativeai as genai
import openai
import os
import json
from datetime import datetime

# Load credentials
def load_credentials():
    creds = {}
    
    # Anthropic (Claude) - should be in environment
    creds['anthropic_key'] = os.getenv('ANTHROPIC_API_KEY')
    
    # Gemini
    gemini_file = os.path.expanduser('~/.openclaw/workspace/credentials/gemini-key.env')
    if os.path.exists(gemini_file):
        with open(gemini_file) as f:
            for line in f:
                if 'GEMINI_API_KEY' in line or 'GOOGLE_API_KEY' in line:
                    creds['gemini_key'] = line.split('=')[1].strip().strip('"\'')
    
    # OpenAI (GPT-4) - check environment
    creds['openai_key'] = os.getenv('OPENAI_API_KEY')
    
    return creds

# Load reel transcript
def load_reel(reel_file):
    with open(reel_file) as f:
        return f.read()

# Load analysis prompt
def load_prompt():
    with open('instagram-intel/tests/analysis_prompt.txt') as f:
        return f.read()

# Run Claude Opus analysis
def analyze_with_opus(prompt, reel_content, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": f"{prompt}\n\nREEL CONTENT:\n{reel_content}"}
        ]
    )
    
    return message.content[0].text

# Run Claude Sonnet analysis
def analyze_with_sonnet(prompt, reel_content, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": f"{prompt}\n\nREEL CONTENT:\n{reel_content}"}
        ]
    )
    
    return message.content[0].text

# Run Gemini analysis
def analyze_with_gemini(prompt, reel_content, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    response = model.generate_content(
        f"{prompt}\n\nREEL CONTENT:\n{reel_content}"
    )
    
    return response.text

# Run GPT-4 analysis
def analyze_with_gpt4(prompt, reel_content, api_key):
    client = openai.OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": f"{prompt}\n\nREEL CONTENT:\n{reel_content}"}
        ],
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def main():
    print("🚀 Starting Model Comparison Test...")
    
    # Load everything
    creds = load_credentials()
    prompt = load_prompt()
    
    reels = [
        'instagram-intel/tests/reels/reel_1_unboxify.txt',
        'instagram-intel/tests/reels/reel_2_trial_concept.txt',
        'instagram-intel/tests/reels/reel_3_spam_calls.txt'
    ]
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'reels': []
    }
    
    for reel_file in reels:
        print(f"\n📊 Analyzing: {reel_file}")
        reel_content = load_reel(reel_file)
        reel_name = os.path.basename(reel_file).replace('.txt', '')
        
        reel_results = {
            'reel': reel_name,
            'models': {}
        }
        
        # Claude Opus
        if creds.get('anthropic_key'):
            print("  🧠 Running Claude Opus...")
            try:
                reel_results['models']['claude_opus'] = analyze_with_opus(
                    prompt, reel_content, creds['anthropic_key']
                )
                print("  ✅ Opus complete")
            except Exception as e:
                print(f"  ❌ Opus failed: {e}")
                reel_results['models']['claude_opus'] = f"ERROR: {str(e)}"
        
        # Claude Sonnet
        if creds.get('anthropic_key'):
            print("  🧠 Running Claude Sonnet...")
            try:
                reel_results['models']['claude_sonnet'] = analyze_with_sonnet(
                    prompt, reel_content, creds['anthropic_key']
                )
                print("  ✅ Sonnet complete")
            except Exception as e:
                print(f"  ❌ Sonnet failed: {e}")
                reel_results['models']['claude_sonnet'] = f"ERROR: {str(e)}"
        
        # Gemini
        if creds.get('gemini_key'):
            print("  🔮 Running Gemini 1.5 Pro...")
            try:
                reel_results['models']['gemini_pro'] = analyze_with_gemini(
                    prompt, reel_content, creds['gemini_key']
                )
                print("  ✅ Gemini complete")
            except Exception as e:
                print(f"  ❌ Gemini failed: {e}")
                reel_results['models']['gemini_pro'] = f"ERROR: {str(e)}"
        
        # GPT-4
        if creds.get('openai_key'):
            print("  🤖 Running GPT-4...")
            try:
                reel_results['models']['gpt4'] = analyze_with_gpt4(
                    prompt, reel_content, creds['openai_key']
                )
                print("  ✅ GPT-4 complete")
            except Exception as e:
                print(f"  ❌ GPT-4 failed: {e}")
                reel_results['models']['gpt4'] = f"ERROR: {str(e)}"
        
        results['reels'].append(reel_results)
    
    # Save results
    output_file = 'instagram-intel/tests/model_comparison_raw.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    print("\n🎯 Next: Run synthesis with Opus to combine insights")
    
    return results

if __name__ == '__main__':
    main()
