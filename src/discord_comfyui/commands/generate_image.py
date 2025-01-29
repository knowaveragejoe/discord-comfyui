"""
Generate image command implementation
"""

import logging
import discord
from discord import app_commands
from ..comfyui import ComfyUIClient
from .base import BaseCommand

# Configure logging
logger = logging.getLogger(__name__)

# Constants
EMBED_COLOR_PROCESSING = discord.Color.orange()
EMBED_COLOR_COMPLETE = discord.Color.dark_green()
EMBED_COLOR_ERROR = discord.Color.red()

class GenerateImageCommand(BaseCommand):
    """Command to generate images using ComfyUI workflows"""
    
    def register(self, tree: app_commands.CommandTree, guild: discord.Object):
        """Register the command with the bot's command tree"""
        
        @tree.command(
            name="gen_image",
            description="Generate an image using a specific workflow",
            guild=guild
        )
        async def genimg(
            interaction: discord.Interaction,
            workflow_name: str,
            prompt: str
        ):
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
                
            # Get the lock for this user
            async with self.bot.get_user_lock(interaction.user.id):
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
                    
                    client = ComfyUIClient(self.bot.config.comfyui.host)

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
