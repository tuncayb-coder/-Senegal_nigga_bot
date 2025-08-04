#!/usr/bin/env python3
"""
Main entry point for the Telegram AI Assistant Bot
"""
import logging
import os
from bot import TelegramAIBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Initialize and start the bot
        bot = TelegramAIBot()
        logger.info("Starting Telegram AI Assistant Bot...")
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
