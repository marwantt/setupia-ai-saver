# Reddit API Setup for Better Downloads

## 🚀 **Why Add Reddit API Access?**

✅ **No Rate Limits** - Download without delays  
✅ **Better Quality** - Access to original resolution  
✅ **Faster Downloads** - Direct media URLs  
✅ **More Reliable** - Official API vs web scraping  

## 📋 **Setup Instructions:**

### 1. **Create Reddit App:**
1. Go to: https://www.reddit.com/prefs/apps
2. Click **"Create App"** or **"Create Another App"**
3. Fill in the form:
   - **Name**: `Setupia AI Saver`
   - **App type**: Select **"script"**
   - **Description**: `Personal media downloader bot`
   - **About URL**: (leave blank)
   - **Redirect URI**: `http://localhost:8080`

### 2. **Get Your Credentials:**
1. After creating, you'll see your app listed
2. **Client ID**: The string under your app name (e.g., `abc123def456`)
3. **Client Secret**: The longer string labeled "secret"

### 3. **Add to Bot Configuration:**

Add these lines to your `.env` file:
```bash
# Reddit API Configuration
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=SetupiaAISaver/1.0
```

### 4. **Example `.env` file:**
```bash
BOT_TOKEN=7963774785:AAHBSOEAoxVTPXUCo47kZmvdh--xySjtN0I
REDDIT_CLIENT_ID=abc123def456
REDDIT_CLIENT_SECRET=xyz789uvw012-LongSecretString
REDDIT_USER_AGENT=SetupiaAISaver/1.0
```

## 🎯 **Benefits After Setup:**

- **Reddit Videos**: Download without timeouts
- **High Quality**: Original resolution images/videos  
- **No Rate Limits**: Process multiple Reddit links quickly
- **Better Metadata**: Full post information and descriptions

## ⚡ **Testing:**

After setup, the bot will automatically use Reddit API for:
- `reddit.com/r/...` links
- `redd.it/...` shortened links

You'll see this log message: `"Using Reddit API credentials for better access"`

## 🔧 **Troubleshooting:**

❌ **Still getting rate limits?**
- Check your credentials are correct
- Make sure app type is "script"
- Restart the bot after adding credentials

❌ **"Invalid credentials" error?**
- Double-check Client ID and Secret
- Ensure no extra spaces in .env file
- Verify app is "script" type, not "web app"

With Reddit API access, your bot will handle Reddit content **much more reliably!** 🚀
