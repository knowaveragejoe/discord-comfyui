"""
System stats command implementation
"""

import logging
import discord
from discord import app_commands
from discord_comfyui.comfyui import ComfyUIClient
from discord_comfyui.commands.base import BaseCommand

# Configure logging
logger = logging.getLogger(__name__)

# Constants
EMBED_COLOR_COMPLETE = discord.Color.dark_green()
EMBED_COLOR_ERROR = discord.Color.red()

class SystemStatsCommand(BaseCommand):
    """Command to get system statistics from ComfyUI server"""
    
    def register(self, tree: app_commands.CommandTree, guild: discord.Object):
        """Register the command with the bot's command tree"""
        
        @tree.command(
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
            
            client = ComfyUIClient(self.bot.config.comfyui.host)
            
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
            except Exception as e:
                logger.error("Failed to get system stats", exc_info=e)
                embed = discord.Embed(
                    title="Error",
                    description=f"Failed to get system stats: {str(e)}",
                    color=EMBED_COLOR_ERROR
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            await client.close()
