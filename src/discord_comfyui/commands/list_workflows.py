"""
List workflows command implementation
"""

import logging
from pathlib import Path
import discord
from discord import app_commands
from discord_comfyui.commands.base import BaseCommand

# Configure logging
logger = logging.getLogger(__name__)

class ListWorkflowsCommand(BaseCommand):
    """Command to list available workflows in ComfyUI"""
    
    def register(self, tree: app_commands.CommandTree, guild: discord.Object):
        """Register the command with the bot's command tree"""
        
        @tree.command(
            name="list_workflows",
            description="List available workflows in ComfyUI",
            guild=guild
        )
        async def list_workflows(interaction: discord.Interaction):
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
                
            # Get the lock for this user
            async with self.bot.get_user_lock(interaction.user.id):
                # Get list of workflow files
                workflows_dir = Path("workflows")
                workflows = [f.name for f in workflows_dir.glob("*.json")]
                workflow_list = "\n".join(workflows) if workflows else "No workflow files found"
                
                embed = discord.Embed(
                    title="Available Workflows",
                    description=workflow_list,
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
