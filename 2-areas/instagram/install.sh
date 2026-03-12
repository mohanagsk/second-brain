#!/bin/bash
# ContentRadar Installation Script

set -e

echo "=================================================="
echo "ContentRadar Installation"
echo "=================================================="
echo ""

# 1. Check Python version
echo "🐍 Checking Python version..."
python3 --version
echo ""

# 2. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt
echo "   ✅ Python packages installed"
echo ""

# 3. Check system dependencies
echo "🔧 Checking system dependencies..."

if ! command -v ffmpeg &> /dev/null; then
    echo "   ⚠️  ffmpeg not found"
    echo "   Install with: sudo apt-get install ffmpeg"
else
    echo "   ✅ ffmpeg installed"
fi

if ! command -v yt-dlp &> /dev/null; then
    echo "   ⚠️  yt-dlp not found"
    echo "   Install with: sudo apt-get install yt-dlp"
else
    echo "   ✅ yt-dlp installed"
fi

echo ""

# 4. Check credentials
echo "🔑 Checking credentials..."

CREDS_DIR="$HOME/.openclaw/workspace/credentials"

if [ -f "$CREDS_DIR/apify-creds.env" ]; then
    echo "   ✅ Apify credentials found"
else
    echo "   ❌ Apify credentials missing: $CREDS_DIR/apify-creds.env"
fi

if [ -f "$CREDS_DIR/gemini-key.env" ]; then
    echo "   ✅ Gemini credentials found"
else
    echo "   ❌ Gemini credentials missing: $CREDS_DIR/gemini-key.env"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "   ⚠️  ANTHROPIC_API_KEY not set in environment"
    echo "      Export with: export ANTHROPIC_API_KEY=your_key"
else
    echo "   ✅ Claude API key set"
fi

if [ -z "$GROQ_API_KEY" ]; then
    echo "   ⚠️  GROQ_API_KEY not set in environment"
    echo "      Export with: export GROQ_API_KEY=your_key"
else
    echo "   ✅ Groq API key set"
fi

echo ""

# 5. Validate setup
echo "✓ Running validation tests..."
python3 test_setup.py

echo ""
echo "=================================================="
echo "Installation complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit config/watchlist.yaml to add creators"
echo "2. Set missing environment variables (see above)"
echo "3. Run: python src/daily_scan.py"
echo ""
