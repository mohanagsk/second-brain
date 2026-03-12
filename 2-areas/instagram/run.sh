#!/bin/bash
# ContentRadar Daily Scan Launcher

set -e

echo "🎯 ContentRadar Daily Scan"
echo "=========================="
echo ""

# Check if we're in the right directory
if [ ! -f "src/daily_scan.py" ]; then
    echo "❌ Error: Must be run from instagram-intel directory"
    echo "   cd /home/divykairoth/.openclaw/workspace/instagram-intel"
    echo "   ./run.sh"
    exit 1
fi

# Load credentials from workspace
CREDS_DIR="$HOME/.openclaw/workspace/credentials"

# Gemini
if [ -f "$CREDS_DIR/gemini-key.env" ]; then
    source "$CREDS_DIR/gemini-key.env"
    echo "✅ Loaded Gemini credentials"
fi

# Check required env vars
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
    echo "   Set with: export ANTHROPIC_API_KEY=your_key"
fi

if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  Warning: GROQ_API_KEY not set"
    echo "   Set with: export GROQ_API_KEY=your_key"
fi

echo ""
echo "🚀 Starting daily scan..."
echo ""

# Run the scan
cd src
python3 daily_scan.py

echo ""
echo "✅ Scan complete!"
echo ""
echo "📁 Check results:"
echo "   - Swipe files: data/swipe_files/"
echo "   - Reports: data/reports/"
echo ""

# Check for alerts
if [ -f "../data/telegram_alert.txt" ]; then
    echo "🚨 Major outliers detected! Alert file generated:"
    echo "   data/telegram_alert.txt"
    echo ""
    echo "   Send to Telegram with:"
    echo "   cat data/telegram_alert.txt | openclaw message send --target=-1003763057831 --thread=86"
    echo ""
fi
