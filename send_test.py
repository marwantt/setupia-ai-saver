#!/usr/bin/env python3

import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def send_test_message():
    """Send a test message to verify bot is working"""
    bot = Bot(os.getenv('BOT_TOKEN'))

    try:
        # Get bot info
        me = await bot.get_me()
        print(f"✅ Connected to: {me.first_name} (@{me.username})")

        # Try to get updates to see if anyone has messaged
        updates = await bot.get_updates()
        print(f"📬 Total updates available: {len(updates)}")

        if updates:
            print("\nRecent messages:")
            for i, update in enumerate(updates[-5:], 1):
                if update.message:
                    user = update.message.from_user
                    text = update.message.text
                    print(f"   {i}. {user.first_name}: {text}")

        print(f"\n🔗 Bot Link: https://t.me/{me.username}")
        print(f"📱 Search for: @{me.username}")
        print(f"💬 Send: /start")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_message())