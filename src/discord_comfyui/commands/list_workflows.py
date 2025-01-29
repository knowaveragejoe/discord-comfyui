"""
List workflows command implementation
"""

import logging
import discord
from discord import app_commands
from .base import BaseCommand

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
                # Placeholder for actual implementation
                workflows = ["Workflow 1", "Workflow 2", "Workflow 3"]
                workflow_list = "\n".join(workflows)
                
                embed = discord.Embed(
                    title="Available Workflows (placeholder)",
                    description=workflow_list,
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
