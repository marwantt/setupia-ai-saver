#!/usr/bin/env python3

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    logger.info(f"📩 START command from: {update.effective_user.first_name} (@{update.effective_user.username})")

    welcome_message = """🤖 **Setupia AI Saver**

✅ **Bot is ready!**

Just send me any URL and I'll download it for you!"""

    try:
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        logger.info("✅ Welcome message sent successfully!")
    except Exception as e:
        logger.error(f"❌ Error sending welcome message: {e}")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo any message to confirm bot is working"""
    user = update.effective_user
    text = update.message.text

    logger.info(f"📩 Message from {user.first_name}: {text}")

    response = f"✅ **Bot is working!**\n\nYou sent: `{text}`\n\n_Send a URL to download media!_"

    try:
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        logger.info("✅ Echo response sent!")
    except Exception as e:
        logger.error(f"❌ Error sending response: {e}")

async def main():
    """Start the bot"""
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("❌ No BOT_TOKEN found in .env file")
        return

    print("🚀 Starting Simple Setupia AI Saver...")
    print(f"🔗 Bot: @SetupiaSaverBot")
    print("📱 Send /start to test!")

    # Create application
    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    # Start polling
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        # Keep running
        await asyncio.Future()  # Run forever

    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())