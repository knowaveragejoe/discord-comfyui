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
from discord import app_commands
from discord_comfyui.comfyui import ComfyUIClient
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
    port: Optional[int] = None
    
    @property
    def websocket_url(self) -> str:
        """Get the WebSocket URL for ComfyUI server"""
        base_url = f"ws://{self.host}"
        return f"{base_url}:{self.port}/ws" if self.port is not None else f"{base_url}/ws"
    
    @property
    def api_url(self) -> str:
        """Get the base HTTP API URL for ComfyUI server"""
        base_url = f"http://{self.host}"
        return f"{base_url}:{self.port}" if self.port is not None else base_url

@dataclass
class BotConfig:
    """Main bot configuration including Discord and ComfyUI settings"""
    token: str
    guild_id: int
    client_id: int
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
            client_id=int(data['client_id']),
            comfyui=ComfyUIConfig(
                host=data['comfyui']['host'],
                port=int(data['comfyui']['port']) if 'port' in data['comfyui'] else None
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
            scopes=("bot", "applications.commands")  # Added applications.commands scope
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
        
        # Set up slash commands
        guild = discord.Object(id=self.config.guild_id)

        @self.tree.command(
            name="get_system_stats",
            description="Get system statistics from ComfyUI server",
            guild=guild
        )
        async def get_system_stats(interaction: discord.Interaction):
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
            
            client = ComfyUIClient(self.config.comfyui.host)
            
            try:
                stats = await client.get_system_stats()
                
                # Create an embed with the system stats
                embed = discord.Embed(
                    title="ComfyUI System Statistics",
                    color=EMBED_COLOR_COMPLETE
                )
                
                # Add fields for each stat category
                for category, values in stats.items():
                    if isinstance(values, dict):
                        # If the value is a nested dict, format it nicely
                        value_str = "\n".join(f"{k}: {v}" for k, v in values.items())
                    else:
                        value_str = str(values)
                    embed.add_field(
                        name=category.replace("_", " ").title(),
                        value=f"```{value_str}```",
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed)
                client.close()
                
            except Exception as e:
                logger.error("Failed to get system stats", exc_info=e)
                embed = discord.Embed(
                    title="Error",
                    description=f"Failed to get system stats: {str(e)}",
                    color=EMBED_COLOR_ERROR
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                client.close()

        @self.tree.command(
            name="list_models",
            description="List available workflows in ComfyUI@aristotle",
            guild=guild
        )
        async def list_models(interaction: discord.Interaction, model_type: str):
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
            
            client = ComfyUIClient(self.config.comfyui.host)

            models = await client.list_models(model_type)

            model_list = "\n".join(models)

            async with self.get_user_lock(interaction.user.id):
                # Create initial response embed
                embed = discord.Embed(
                    title=f"List of {model_type} available:",
                    description=model_list,
                    color=EMBED_COLOR_PROCESSING
                )
                await interaction.response.send_message(embed=embed)
                client.close()
            
        @self.tree.command(
            name="list_workflows",
            description="List available workflows in ComfyUI@aristotle",
            guild=guild
        )
        async def list_workflows(interaction: discord.Interaction):
            """List available workflows from ComfyUI"""
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
                
            # Get the lock for this user
            async with self.get_user_lock(interaction.user.id):
                # Placeholder for actual implementation
                workflows = ["Workflow 1", "Workflow 2", "Workflow 3"]
                workflow_list = "\n".join(workflows)
                
                embed = discord.Embed(
                    title="Available Workflows (placeholder)",
                    description=workflow_list,
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)

        @self.tree.command(
            name="gen_image",
            description="Generate an image using a specific workflow",
            guild=guild
        )
        async def genimg(
            interaction: discord.Interaction,
            workflow_name: str,
            prompt: str
        ):
            """Generate an image using the specified workflow and prompt"""
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
                
            # Get the lock for this user
            async with self.get_user_lock(interaction.user.id):
                # Create initial response embed
                embed = discord.Embed(
                    title="Generating Image",
                    description=f"Using workflow: {workflow_name}\nProcessing prompt: {prompt}",
                    color=EMBED_COLOR_PROCESSING
                )
                await interaction.response.send_message(embed=embed)
                
                try:
                    # TODO: Implement ComfyUI WebSocket connection and image generation
                    logger.info(f"Image generation requested by {interaction.user} (ID: {interaction.user.id})")
                    logger.info(f"Workflow: {workflow_name}")
                    logger.info(f"Prompt: {prompt}")
                    
                    client = ComfyUIClient(self.config.comfyui.host)

                    # Placeholder for actual implementation
                    await client.queue_prompt(prompt)
                    
                    embed.color = EMBED_COLOR_COMPLETE
                    embed.description = f"Generated image using workflow '{workflow_name}' with prompt: {prompt}\n(Image generation not yet implemented)"
                    await interaction.edit_original_response(embed=embed)
                    
                except Exception as e:
                    logger.error("Image generation failed", exc_info=e)
                    embed.color = EMBED_COLOR_ERROR
                    embed.description = f"Failed to generate image: {str(e)}"
                    await interaction.edit_original_response(embed=embed)
        
        # Sync the command tree
        await self.tree.sync(guild=guild)
        logger.info("Slash commands synced with Discord")
        
        logger.info("Bot setup complete")
        
    def get_user_lock(self, user_id: int) -> asyncio.Lock:
        """Get or create a lock for a specific user's generations"""
        if user_id not in self._generation_locks:
            self._generation_locks[user_id] = asyncio.Lock()
        return self._generation_locks[user_id]
    
    def check_interaction_permissions(self, interaction: discord.Interaction) -> tuple[bool, Optional[str]]:
        """Check if the interaction meets channel and role restrictions
        
        Args:
            interaction: The Discord interaction to check
            
        Returns:
            A tuple of (passed, error_message) where passed is True if all checks passed,
            and error_message contains the failure reason if passed is False
        """
        # Check channel restrictions
        if self.config.allowed_channels and interaction.channel_id not in self.config.allowed_channels:
            return False, "This command can only be used in specific channels."
                
        # Check role restrictions
        if self.config.allowed_roles and not any(
            role.id in self.config.allowed_roles for role in interaction.user.roles
        ):
            return False, "You don't have the required role to use this command."
        
        return True, None
        
    async def on_ready(self):
        """Called when the bot has connected to Discord"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"ComfyUI websocked configured at: {self.config.comfyui.websocket_url}")
        
        if self.config.allowed_channels:
            channels = [str(ch) for ch in self.config.allowed_channels]
            logger.info(f"Bot restricted to channels: {', '.join(channels)}")
            
        if self.config.allowed_roles:
            roles = [str(r) for r in self.config.allowed_roles]
            logger.info(f"Bot restricted to roles: {', '.join(roles)}")

def load_bot() -> ComfyUIBot:
    """Load the bot with configuration from config.yaml"""
    # Get the project root directory (where config.yaml should be)
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / 'config.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at: {config_path}\n"
            "Please create one from config.yaml.template"
        )
    
    config = BotConfig.from_yaml(config_path)
    return ComfyUIBot(config)
