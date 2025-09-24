# 🚂 Railway Environment Variables Setup

## 🚨 **Issue:** BOT_TOKEN not found in environment variables

### **Why This Happens:**
- ✅ `.env` file is **correctly excluded** from GitHub (security)
- ❌ Railway doesn't have the **BOT_TOKEN** environment variable
- 🔧 Must add environment variables in Railway dashboard

## 🔧 **SOLUTION - Step by Step:**

### **Step 1: Access Railway Dashboard**
1. Go to: **https://railway.app**
2. Login with your GitHub account
3. Find your **"setupia-ai-saver"** project
4. Click on it to open

### **Step 2: Add Environment Variables**
1. In your project dashboard, click **"Variables"** tab
2. Click **"+ New Variable"** button
3. Add the bot token:
   - **Name**: `BOT_TOKEN`
   - **Value**: `7963774785:AAHBSOEAoxVTPXUCo47kZmvdh--xySjtN0I`
4. Click **"Add"**

### **Step 3: Add Instagram Support (Optional)**
If you want Instagram support later:
- **Name**: `INSTAGRAM_COOKIES_FILE`
- **Value**: `./cookies/instagram_cookies.txt`

### **Step 4: Auto-Redeploy**
- Railway will **automatically redeploy** after adding variables
- Wait ~1-2 minutes for deployment to complete
- Check logs for "✅ Bot connected successfully!"

## 🔍 **Verify Setup:**

### **Check Deployment Logs:**
1. In Railway dashboard, go to **"Deployments"** tab
2. Click on latest deployment
3. Check logs for:
   - ✅ `🚀 Starting Setupia AI Saver bot...`
   - ✅ `Bot: @SetupiaSaverBot`
   - ✅ `Ready to receive URLs!`

### **Test Bot:**
1. Open Telegram
2. Search: `@SetupiaSaverBot`
3. Send: `/start`
4. Should get welcome message immediately!

## 🛠 **Troubleshooting:**

### **Still getting BOT_TOKEN error?**
- Double-check variable name is exactly: `BOT_TOKEN`
- Verify token value is complete (no extra spaces)
- Wait 2-3 minutes for redeploy to complete

### **Bot not responding?**
- Check Railway logs for errors
- Verify bot token is correct
- Ensure deployment is "Active" status

### **Variables Not Saving?**
- Make sure you clicked "Add" after entering
- Refresh Railway dashboard page
- Try adding variables one at a time

## ✅ **Expected Result:**

After adding BOT_TOKEN:
- ✅ Bot starts successfully on Railway
- ✅ No more "BOT_TOKEN not found" errors
- ✅ Bot responds to `/start` on Telegram
- ✅ Ready to download media from phone!

## 🔒 **Security Note:**

✅ **Good Practice:**
- `.env` files stay local (not in GitHub)
- Environment variables in Railway dashboard
- Bot token kept secure

❌ **Never:**
- Commit `.env` files to GitHub
- Share bot tokens publicly
- Hardcode tokens in source code

**Once BOT_TOKEN is added, your bot will work perfectly from your phone!** 📱🚀
