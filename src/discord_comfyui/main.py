"""
Main entry point for the Discord ComfyUI bot
"""

import asyncio
import logging
import sys
from pathlib import Path

from .bot import load_bot

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the bot"""
    try:
        # Load and start the bot (config validation happens in load_bot)
        bot = load_bot()
        asyncio.run(bot.start(bot.config.token))
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}", exc_info=e)
        sys.exit(1)

if __name__ == "__main__":
    main()
