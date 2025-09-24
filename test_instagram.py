#!/usr/bin/env python3
"""
Instagram Cookie Test Script
Tests if Instagram cookies are working properly
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_instagram_cookies():
    """Test Instagram cookies configuration"""
    print("🍪 Instagram Cookies Test")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    cookies_file = os.getenv('INSTAGRAM_COOKIES_FILE')
    
    if not cookies_file:
        print("❌ INSTAGRAM_COOKIES_FILE not configured in .env")
        return False
        
    cookies_path = Path(cookies_file)
    print(f"Cookies file: {cookies_file}")
    print(f"File exists: {cookies_path.exists()}")
    
    if not cookies_path.exists():
        print()
        print("📋 To add cookies:")
        print("1. Install 'Get cookies.txt LOCALLY' Chrome extension")
        print("2. Login to Instagram")
        print("3. Export cookies")
        print(f"4. Save as: {cookies_file}")
        return False
    
    # Test with gallery-dl
    print("\n🧪 Testing cookies with gallery-dl...")
    test_url = "https://www.instagram.com/stories/azyzsmida/3728876191093667747/"
    
    try:
        cmd = [
            'gallery-dl',
            '--cookies', str(cookies_path),
            '--simulate',
            test_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Cookies working! Instagram content accessible")
            print("✅ Bot will now download Instagram stories/posts")
            return True
        else:
            error = result.stderr.lower()
            if 'authreq' in error or 'login' in error:
                print("❌ Cookies not working - authentication still required")
                print("💡 Try re-exporting fresh cookies from your browser")
            else:
                print(f"❌ Test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out - may be network issue")
        return False
    except FileNotFoundError:
        print("❌ gallery-dl not found - run from bot environment")
        return False

if __name__ == "__main__":
    print("🤖 Setupia AI Saver - Instagram Test")
    print()
    
    success = test_instagram_cookies()
    
    if success:
        print("\n🎉 Instagram authentication is working!")
        print("📱 You can now download Instagram stories and posts")
    else:
        print("\n📖 See INSTAGRAM_PERMISSION.md for setup help")
    
    sys.exit(0 if success else 1)
