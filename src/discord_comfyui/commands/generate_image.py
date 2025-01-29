"""
Generate image command implementation
"""
import asyncio
import logging
import json
import os
from pathlib import Path
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
    def __init__(self, bot):
        super().__init__(bot)
        self._running = False
    
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
            prompt: str,
            negative_prompt: str = None
        ):
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
            
            if self._running:
                await interaction.response.send_message("Another image generation is already in progress", ephemeral=True)
                return
            else:
                self._running = True
                
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
                    # Find and load the workflow file
                    workflow_path = None
                    workflows_dir = Path("workflows")
                    for file in workflows_dir.glob("*.json"):
                        if file.stem == workflow_name:
                            workflow_path = file
                            break
                    
                    if not workflow_path:
                        raise ValueError(f"Workflow '{workflow_name}' not found")
                    
                    # Load and parse the workflow JSON
                    with open(workflow_path) as f:
                        workflow_data = json.load(f)
                    
                    # Extract node names
                    node_descriptions = []
                    for node_id, node_info in workflow_data.items():
                        node_descriptions.append(f"Node {node_id}: {node_info['class_type']} - {node_info.get('_meta').get('title')}")
                    
                    # Update embed with workflow information
                    embed.add_field(
                        name="Workflow Nodes",
                        value="\n".join(node_descriptions),
                        inline=False
                    )

                    # sleep for 5 seconds to simulate image generation
                    await asyncio.sleep(5)
                    
                    logger.info(f"Image generation requested by {interaction.user} (ID: {interaction.user.id})")
                    logger.info(f"Workflow: {workflow_name}")
                    logger.info(f"Prompt: {prompt}")
                    
                    client = ComfyUIClient(self.bot.config.comfyui.host)

                    # Placeholder for actual implementation
                    # await client.queue_prompt(prompt)
                    
                    embed.color = EMBED_COLOR_COMPLETE
                    embed.description = f"Generated image using workflow '{workflow_name}' with prompt: {prompt}\n(Image generation not yet implemented)"
                    await interaction.edit_original_response(embed=embed)
                    await client.close()
                    
                except Exception as e:
                    logger.error("Image generation failed", exc_info=e)
                    embed.color = EMBED_COLOR_ERROR
                    embed.description = f"Failed to generate image: {str(e)}"
                    await interaction.edit_original_response(embed=embed)
                    await client.close()
                
                self._running = False

