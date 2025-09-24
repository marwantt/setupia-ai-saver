#!/bin/bash

# Setupia AI Saver - Run Script

echo "🚀 Starting Setupia AI Saver Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Upgrade yt-dlp and gallery-dl to latest versions
echo "Updating yt-dlp and gallery-dl to latest versions..."
pip install --upgrade yt-dlp gallery-dl

# Run the bot
echo "Starting bot..."
python bot.py