"""
Generate image command implementation
"""
import logging
import io
import discord
from discord import app_commands
from discord_comfyui.comfyui import ComfyUIClient
from discord_comfyui.commands.base import BaseCommand
from discord_comfyui.generation_request import GenerationRequest

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
            
            # Lock image generation to one at a time
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
                    # Create and process the generation request
                    generation_request = GenerationRequest(
                        prompt=prompt,
                        workflow_name=workflow_name,
                        negative_prompt=negative_prompt
                    )
                    
                    # # Update embed with workflow information
                    # embed.add_field(
                    #     name="Workflow Nodes",
                    #     value="\n".join(generation_request.get_node_descriptions()),
                    #     inline=False
                    # )
                    
                    logger.info(f"Image generation requested by {interaction.user} (ID: {interaction.user.id})")
                    logger.info(f"Workflow: {workflow_name}")
                    logger.info(f"Prompt: {prompt}")
                    logger.info(f"Negative prompt: {negative_prompt}")
                    
                    # connect to the ComfyUI instance
                    client = ComfyUIClient(self.bot.config.comfyui.host)
                    await client.connect()

                    # trigger the prompt
                    response = await client.queue_prompt(generation_request.workflow_json)

                    # save the prompt ID that ComfyUI returns
                    generation_request.prompt_id = response["prompt_id"]
                    logger.info(f"Queued prompt with ID: {generation_request.prompt_id}")

                    # Track the execution progress & get the image filename
                    image_filename = await self.track_progress(
                        client=client, 
                        generation_request=generation_request,
                        interaction=interaction, 
                        embed=embed
                    )

                    logger.info(f"Image generation complete. Retrieving image: {image_filename}")

                    # Retrieve the generated image
                    image_data = await client.get_image(filename=image_filename, folder_type="output")
                    logger.info(f"Image data retrieved: {len(image_data)} bytes")
                    
                    # Create a BytesIO object from the image data
                    image_io = io.BytesIO(image_data)
                    # Create a discord File object from the BytesIO
                    file = discord.File(fp=image_io, filename="generated_image.png")
                    
                    embed.color = EMBED_COLOR_COMPLETE
                    embed.description = f"Generated image using workflow '{workflow_name}' with prompt: {prompt}"
                    embed.set_image(url="attachment://generated_image.png")
                    
                    await interaction.edit_original_response(embed=embed, attachments=[file])
                    await client.close()
                    
                except Exception as e:
                    logger.error("Image generation failed", exc_info=e)
                    embed.color = EMBED_COLOR_ERROR
                    embed.description = f"Failed to generate image: {str(e)}"
                    await interaction.edit_original_response(embed=embed)
                    await client.close()
                
                self._running = False

    async def track_progress(self,
        client: ComfyUIClient,
        generation_request: GenerationRequest,
        interaction: discord.Interaction,
        embed: discord.Embed
    ):
        # Callback handler to update embed
        async def progress_callback(data):
            if data["type"] == "progress":
                progress = data["data"]
                value = progress["value"]
                max_value = progress["max"]
                percentage = int((value / max_value) * 20)  # 20 segments for progress bar
                progress_bar = "█" * percentage + "░" * (20 - percentage)
                progress_text = f"[{progress_bar}] {value}/{max_value}"
                
                embed.description = (
                    f"Using workflow: {generation_request.workflow_name}\n"
                    f"Processing prompt: {generation_request.prompt}\n"
                    f"Progress: {progress_text}"
                )
                await interaction.edit_original_response(embed=embed)

        # Track the execution progress
        logger.info(f"Tracking progress for prompt {generation_request.prompt_id}....")
        image_filename = await client.track_progress(generation_request.prompt_id, callback=progress_callback)

        return image_filename
