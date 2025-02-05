"""
Interrupt prompt processing
"""

import logging
import discord
from discord import app_commands
from discord_comfyui.comfyui import ComfyUIClient
from discord_comfyui.commands.base import BaseCommand

# Configure logging
logger = logging.getLogger(__name__)

# Constants
EMBED_COLOR_PROCESSING = discord.Color.orange()

class StopCommand(BaseCommand):
    """Command to list available models in ComfyUI"""
    
    def register(self, tree: app_commands.CommandTree, guild: discord.Object):
        """Register the command with the bot's command tree"""
        
        @tree.command(
            name="stop",
            description="Stop any other processing in flight",
            guild=guild
        )
        async def stop(interaction: discord.Interaction):
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
            
            client = ComfyUIClient(self.bot.config.comfyui.host)

            response = await client.interrupt()

            async with self.bot.get_user_lock(interaction.user.id):
                # Create initial response embed
                embed = discord.Embed(
                    title=f"Processing stopped.",
                    color=EMBED_COLOR_PROCESSING
                )
                await interaction.response.send_message(embed=embed)
                await client.close()
