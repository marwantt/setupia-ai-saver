# 🍪 How to Get Instagram Cookies (REQUIRED for Stories)

## 🚨 **Why You Need Cookies:**
Instagram stories require you to be **logged in**. Cookies contain your login session.

## 🔧 **Method 1: Chrome Extension (Easiest)**

### **Step 1: Install Extension**
1. Open Chrome
2. Go to Chrome Web Store
3. Search: **"Get cookies.txt LOCALLY"**
4. Click **"Add to Chrome"**

### **Step 2: Login to Instagram**
1. Go to `https://instagram.com`
2. Login with your account
3. Make sure you can view stories normally

### **Step 3: Export Cookies**
1. **Stay on Instagram page**
2. Click the **extension icon** (usually in toolbar)
3. Click **"Export"** or **"Download"**
4. File will download as `instagram.com_cookies.txt` or similar

### **Step 4: Move to Bot**
```bash
# Move the downloaded file to bot cookies folder
mv ~/Downloads/instagram*.txt "/Users/marwan/Desktop/Setupia AI Saver/cookies/instagram_cookies.txt"
```

## 🔧 **Method 2: Firefox**

1. Install **"cookies.txt"** extension
2. Login to Instagram
3. Click extension → Export
4. Save as `instagram_cookies.txt`

## 🔧 **Method 3: Safari (Manual)**

1. Open **Developer Tools** (F12)
2. Go to **Application** → **Cookies** → `https://instagram.com`
3. Find these important cookies:
   - `sessionid` (your login session)
   - `csrftoken` (security token)

4. Create file manually:
```bash
cat > "/Users/marwan/Desktop/Setupia AI Saver/cookies/instagram_cookies.txt" << 'EOF'
# Netscape HTTP Cookie File
.instagram.com	TRUE	/	TRUE	1735689600	sessionid	YOUR_SESSION_ID_HERE
.instagram.com	TRUE	/	TRUE	1735689600	csrftoken	YOUR_CSRF_TOKEN_HERE
EOF
```

## ✅ **Test Your Setup:**

```bash
cd "/Users/marwan/Desktop/Setupia AI Saver"
source venv/bin/activate

# Test if cookies work
gallery-dl --cookies cookies/instagram_cookies.txt --simulate "https://www.instagram.com/stories/azyzsmida/3728876191093667747/"
```

**Success looks like:**
```
[instagram] Extracting URL: https://www.instagram.com/stories/...
[instagram] story: Downloading JSON metadata
# Story title here
```

**Failure looks like:**
```
[instagram][error] AuthRequired: authenticated cookies needed
```

## 🎯 **After Cookies Are Added:**

Your bot will show:
- ✅ "🔍 Analyzing Instagram content..."
- ✅ "🔐 Authentication required, using cookies..." 
- ✅ "Using Instagram cookies for authentication"
- ✅ Story downloads successfully!

## 🔒 **Important:**
- **Keep cookies private** - they contain your login
- **Don't share** with others
- **Refresh monthly** - cookies expire
- **Only use your own** account cookies

**Once you have cookies, Instagram stories will work perfectly!** 🚀
