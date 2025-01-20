"""
Core Discord bot implementation for ComfyUI integration
"""

import asyncio
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
import yaml

# Configure logging with a consistent format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Constants for message handling and display
EMBED_COLOR_PROCESSING = discord.Color.orange()
EMBED_COLOR_COMPLETE = discord.Color.dark_green()
EMBED_COLOR_ERROR = discord.Color.red()

# The permissions the bot needs to function
BOT_PERMISSIONS = discord.Permissions(
    send_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    manage_messages=True,
)

@dataclass
class ComfyUIConfig:
    """Configuration settings for ComfyUI server connection"""
    host: str 
    port: int
    
    @property
    def websocket_url(self) -> str:
        """Get the WebSocket URL for ComfyUI server"""
        return f"ws://{self.host}:{self.port}/ws"
    
    @property
    def api_url(self) -> str:
        """Get the base HTTP API URL for ComfyUI server"""
        return f"http://{self.host}:{self.port}"

@dataclass
class BotConfig:
    """Main bot configuration including Discord and ComfyUI settings"""
    token: str
    guild_id: int
    client_id: int  # Added client_id field
    comfyui: ComfyUIConfig
    allowed_channels: list[int] = field(default_factory=list)
    allowed_roles: list[int] = field(default_factory=list)
    
    @classmethod
    def from_yaml(cls, path: Path) -> 'BotConfig':
        """Load configuration from a YAML file"""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
        return cls(
            token=data['bot_token'],
            guild_id=int(data['guild_id']),
            client_id=int(data['client_id']),  # Parse client_id from config
            comfyui=ComfyUIConfig(
                host=data['comfyui']['host'],
                port=int(data['comfyui']['port'])
            ),
            allowed_channels=data.get('allowed_channels', []),
            allowed_roles=data.get('allowed_roles', [])
        )
    
    @property
    def invite_url(self) -> str:
        """Generate the bot's invite URL with required permissions"""
        return discord.utils.oauth_url(
            self.client_id,
            permissions=BOT_PERMISSIONS,
            scopes=("bot",)
        )

class ComfyUIBot(commands.Bot):
    """Discord bot with ComfyUI integration"""
    
    def __init__(self, config: BotConfig):
        # Set up intents for message content
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            activity=discord.Game(name="Generating images with ComfyUI")
        )
        
        self.config = config
        self._generation_locks = {}  # User ID to lock mapping
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up ComfyUI Discord bot...")
        
        # Display the invite URL
        logger.info("\nBot Invite URL:")
        logger.info(self.config.invite_url + "\n")
        
        # Register commands
        await self.add_cog(ImageGenerationCommands(self))
        
        logger.info("Bot setup complete")
        
    def get_user_lock(self, user_id: int) -> asyncio.Lock:
        """Get or create a lock for a specific user's generations"""
        if user_id not in self._generation_locks:
            self._generation_locks[user_id] = asyncio.Lock()
        return self._generation_locks[user_id]
        
    async def on_ready(self):
        """Called when the bot has connected to Discord"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"ComfyUI server configured at: {self.config.comfyui.websocket_url}")
        
        if self.config.allowed_channels:
            channels = [str(ch) for ch in self.config.allowed_channels]
            logger.info(f"Bot restricted to channels: {', '.join(channels)}")
            
        if self.config.allowed_roles:
            roles = [str(r) for r in self.config.allowed_roles]
            logger.info(f"Bot restricted to roles: {', '.join(roles)}")

# ... rest of the file remains the same ...
