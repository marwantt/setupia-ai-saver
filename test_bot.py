#!/usr/bin/env python3

import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def test_bot():
    """Test if bot token is valid and bot can connect"""
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("❌ No bot token found")
        return False

    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot name: {me.first_name}")
        print(f"   Username: @{me.username}")
        print(f"   Bot ID: {me.id}")
        return True
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_bot())
    if result:
        print("\n🚀 Bot token is valid and ready to use!")
        print("You can now start the main bot with: python bot.py")
    else:
        print("\n⚠️  Please check your bot token in .env file")