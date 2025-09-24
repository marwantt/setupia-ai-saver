# Setupia AI Saver

A personal Telegram bot for downloading images and videos from various platforms using yt-dlp and gallery-dl.

## Features

- 🎥 Download videos from YouTube, TikTok, and more
- 📸 Download images from Instagram, Twitter, and other social platforms
- 🔤 Formatted descriptions with Geist Mono font
- 📱 Optimized for mobile and desktop use
- 🚀 Easy deployment

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment setup:**
   - Copy `.env.example` to `.env` (already configured with your bot token)

3. **Run the bot:**
   ```bash
   python bot.py
   ```

## Usage

1. Start the bot with `/start`
2. Send any supported URL to download media
3. Get your files with formatted descriptions

## Supported Platforms

- YouTube (yt-dlp)
- Instagram (gallery-dl)
- Twitter/X (gallery-dl)
- TikTok (yt-dlp)
- Many more...

## Deployment Options

### Local Development
```bash
python bot.py
```

### Production (using PM2)
```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

### Docker
```bash
docker build -t setupia-ai-saver .
docker run -d --name setupia-bot setupia-ai-saver
```

## File Structure

```
Setupia AI Saver/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── .gitignore         # Git ignore file
├── Dockerfile         # Docker configuration
├── ecosystem.config.js # PM2 configuration
└── README.md          # This file
```