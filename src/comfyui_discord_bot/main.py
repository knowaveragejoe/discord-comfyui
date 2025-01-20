"""
Main entry point for the ComfyUI Discord Bot
"""

import os
import logging
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from .env file"""
    env_path = Path('.') / '.env'
    if not env_path.exists():
        logger.error("No .env file found. Please create one from .env.template")
        raise FileNotFoundError("No .env file found")
    
    load_dotenv()
    
    required_vars = [
        'DISCORD_TOKEN',
        'DISCORD_GUILD_ID',
        'COMFYUI_HOST',
        'COMFYUI_PORT'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {
        'discord_token': os.getenv('DISCORD_TOKEN'),
        'guild_id': int(os.getenv('DISCORD_GUILD_ID')),
        'comfyui_host': os.getenv('COMFYUI_HOST'),
        'comfyui_port': int(os.getenv('COMFYUI_PORT'))
    }

def main():
    """Main entry point for the bot"""
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        # Initialize bot
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        @bot.event
        async def on_ready():
            logger.info(f"{bot.user} has connected to Discord!")
            logger.info(f"ComfyUI server configured at: {config['comfyui_host']}:{config['comfyui_port']}")
        
        # Start the bot
        bot.run(config['discord_token'])
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

if __name__ == "__main__":
    main()
