#!/usr/bin/env python3
"""
test_setup.py - Validate ContentRadar setup
"""
import os
import sys
from pathlib import Path

def check_system_deps():
    """Check system dependencies"""
    print("🔍 Checking system dependencies...\n")
    
    deps = {
        "ffmpeg": "sudo apt-get install ffmpeg",
        "ffprobe": "sudo apt-get install ffmpeg",
        "yt-dlp": "sudo apt-get install yt-dlp"
    }
    
    missing = []
    for cmd, install in deps.items():
        if os.system(f"which {cmd} > /dev/null 2>&1") != 0:
            print(f"  ❌ {cmd} not found")
            print(f"     Install: {install}\n")
            missing.append(cmd)
        else:
            print(f"  ✅ {cmd} found")
    
    return len(missing) == 0

def check_python_deps():
    """Check Python dependencies"""
    print("\n🔍 Checking Python dependencies...\n")
    
    deps = {
        "yaml": "pyyaml",
        "requests": "requests",
        "anthropic": "anthropic",
        "google.generativeai": "google-generativeai"
    }
    
    missing = []
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n  Install with: pip install {' '.join(missing)}\n")
    
    return len(missing) == 0

def check_credentials():
    """Check API credentials"""
    print("\n🔍 Checking API credentials...\n")
    
    creds_dir = Path.home() / ".openclaw/workspace/credentials"
    
    checks = [
        ("Apify", creds_dir / "apify-creds.env", "APIFY_TOKEN"),
        ("Gemini", creds_dir / "gemini-key.env", "GEMINI_API_KEY"),
        ("Claude", None, "ANTHROPIC_API_KEY"),
        ("Groq", None, "GROQ_API_KEY")
    ]
    
    all_ok = True
    for name, file_path, env_var in checks:
        if file_path:
            if file_path.exists():
                print(f"  ✅ {name} credentials file found")
            else:
                print(f"  ❌ {name} credentials file not found: {file_path}")
                all_ok = False
        else:
            if os.getenv(env_var):
                print(f"  ✅ {name} environment variable set")
            else:
                print(f"  ❌ {name} environment variable not set: {env_var}")
                all_ok = False
    
    return all_ok

def check_modules():
    """Check our modules can be imported"""
    print("\n🔍 Checking ContentRadar modules...\n")
    
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    modules = ["media", "transcribe", "analyze"]
    all_ok = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}.py")
        except Exception as e:
            print(f"  ❌ {module}.py - {e}")
            all_ok = False
    
    return all_ok

def check_config():
    """Check configuration"""
    print("\n🔍 Checking configuration...\n")
    
    config_file = Path(__file__).parent / "config/watchlist.yaml"
    
    if not config_file.exists():
        print(f"  ❌ Config not found: {config_file}")
        return False
    
    print(f"  ✅ Config file found")
    
    try:
        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        creators = config.get('creators', [])
        print(f"  ✅ {len(creators)} creators in watchlist")
        
        for creator in creators:
            print(f"     - @{creator['username']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Config parse error: {e}")
        return False

def main():
    print("="*60)
    print("ContentRadar Setup Validation")
    print("="*60)
    
    results = {
        "System Dependencies": check_system_deps(),
        "Python Dependencies": check_python_deps(),
        "API Credentials": check_credentials(),
        "ContentRadar Modules": check_modules(),
        "Configuration": check_config()
    }
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60 + "\n")
    
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All checks passed! ContentRadar is ready to run.")
        print("="*60)
        print("\nRun: python src/daily_scan.py\n")
        return 0
    else:
        print("❌ Some checks failed. Fix the issues above.")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
