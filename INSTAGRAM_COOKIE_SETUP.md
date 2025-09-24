# 🍪 Instagram Browser Cookies Setup

## 🎯 **What This Enables:**
- ✅ **Instagram Images** - Download photos from posts
- ✅ **Instagram Stories** - Download temporary stories  
- ✅ **Instagram Reels** - Download short videos
- ✅ **High Quality** - Original resolution downloads
- ✅ **Private Posts** - Access posts from accounts you follow

## 📋 **Step-by-Step Setup:**

### **Method 1: Chrome Extension (Recommended)**

1. **Install Extension:**
   - Go to Chrome Web Store
   - Search: "Get cookies.txt LOCALLY"
   - Install the extension

2. **Login to Instagram:**
   - Go to `https://instagram.com`
   - Login to your account
   - Make sure you're logged in successfully

3. **Export Cookies:**
   - Click the extension icon in Chrome
   - Click "Export" 
   - Save as `instagram_cookies.txt`

4. **Move Cookies File:**
   ```bash
   cp ~/Downloads/instagram_cookies.txt "/Users/marwan/Desktop/Setupia AI Saver/cookies/"
   ```

### **Method 2: Firefox**

1. **Install Extension:**
   - Firefox Add-ons: "cookies.txt"
   - Install and enable

2. **Export Process:**
   - Login to Instagram
   - Click extension → Export
   - Save as `instagram_cookies.txt`

### **Method 3: Manual (Advanced)**

1. **Open Browser DevTools:**
   - Press `F12` on Instagram.com
   - Go to `Application` → `Cookies` → `https://instagram.com`

2. **Copy Important Cookies:**
   ```
   sessionid=YOUR_SESSION_ID
   csrftoken=YOUR_CSRF_TOKEN
   ```

3. **Create cookies file:**
   ```bash
   cat > cookies/instagram_cookies.txt << 'EOF'
   # Netscape HTTP Cookie File
   .instagram.com	TRUE	/	TRUE	1735689600	sessionid	YOUR_SESSION_ID_HERE
   .instagram.com	TRUE	/	TRUE	1735689600	csrftoken	YOUR_CSRF_TOKEN_HERE
   EOF
   ```

## 🔧 **Verify Setup:**

```bash
cd "/Users/marwan/Desktop/Setupia AI Saver"
source venv/bin/activate

# Test configuration
python -c "
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

cookies_file = os.getenv('INSTAGRAM_COOKIES_FILE')
print(f'Cookies file: {cookies_file}')
print(f'File exists: {Path(cookies_file).exists() if cookies_file else False}')
"

# Test with gallery-dl
gallery-dl --cookies cookies/instagram_cookies.txt --simulate "https://www.instagram.com/p/DO_sfMlCNR1/"
```

## 📱 **Instagram Stories Support:**

Stories work with the same cookies:

```bash
# Test Instagram story
gallery-dl --cookies cookies/instagram_cookies.txt "https://www.instagram.com/stories/USERNAME/"
```

**Story URL formats:**
- `https://www.instagram.com/stories/username/`
- `https://www.instagram.com/stories/highlights/HIGHLIGHT_ID/`

## 🎯 **Bot Integration:**

With cookies configured, the bot will:

1. **Detect Instagram URLs** ✅
2. **Show**: "📸 Downloading Instagram content..."  
3. **Use cookies automatically** ✅
4. **Download images/stories** ✅
5. **Provide high-quality files** ✅

## 🔒 **Security Notes:**

- **Cookies = Login Session** - Keep private!
- **Don't share** cookies file with anyone
- **Regenerate** if compromised  
- **Expires** - May need to re-export monthly

## 🧪 **Testing:**

After setup, test with bot:

```
# Instagram post (image)
@https://www.instagram.com/p/DO_sfMlCNR1/

# Instagram story  
@https://www.instagram.com/stories/username/

# Instagram reel
@https://www.instagram.com/reel/REEL_ID/
```

Expected bot response:
- ✅ "📸 Downloading Instagram content..."
- ✅ "Using Instagram cookies for authentication"  
- ✅ Download successful

## ❌ **Troubleshooting:**

**Still getting login errors?**
- Re-export fresh cookies
- Check file path in .env
- Verify you're logged into Instagram
- Try different browser

**Stories not working?**
- Stories expire after 24 hours
- Need to follow the account
- Some stories are private/restricted

**With browser cookies, Instagram images and stories will work perfectly!** 🚀📸
