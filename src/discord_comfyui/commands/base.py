"""
Base command class for ComfyUI Discord bot commands
"""

from abc import ABC, abstractmethod
import discord
from discord import app_commands

class BaseCommand(ABC):
    """Base class for bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
        
    def check_interaction_permissions(self, interaction: discord.Interaction) -> tuple[bool, str | None]:
        """Check if the interaction meets channel and role restrictions"""
        # Check channel restrictions
        if self.bot.config.allowed_channels and interaction.channel_id not in self.bot.config.allowed_channels:
            return False, "This command can only be used in specific channels."
                
        # Check role restrictions
        if self.bot.config.allowed_roles and not any(
            role.id in self.bot.config.allowed_roles for role in interaction.user.roles
        ):
            return False, "You don't have the required role to use this command."
        
        return True, None
    
    @abstractmethod
    def register(self, tree: app_commands.CommandTree, guild: discord.Object):
        """Register the command with the bot's command tree"""
        pass
