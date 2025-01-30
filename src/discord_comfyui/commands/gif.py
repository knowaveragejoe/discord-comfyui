"""
GIF command implementation for retrieving Giphy GIFs
"""
import logging
import random
import aiohttp
import discord
from discord import app_commands
from discord_comfyui.commands.base import BaseCommand

# Configure logging
logger = logging.getLogger(__name__)

class GifCommand(BaseCommand):
    """Command to fetch GIFs from Giphy"""
    
    def register(self, tree: app_commands.CommandTree, guild: discord.Object):
        """Register the command with the bot's command tree"""
        
        @tree.command(
            name="gif",
            description="Get a random Deanna Troi GIF",
            guild=guild
        )
        async def gif(interaction: discord.Interaction):
            # Check permissions
            passed, error_message = self.check_interaction_permissions(interaction)
            if not passed:
                await interaction.response.send_message(error_message, ephemeral=True)
                return
            
            try:
                # Create initial response embed
                embed = discord.Embed(
                    title="Fetching GIF...",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
                
                # Get Giphy API key from config
                api_key = self.bot.config.giphy.api_key
                
                # Construct Giphy API URL
                search_term = "deanna troi"
                base_url = "https://api.giphy.com/v1/gifs/search"
                params = {
                    "api_key": api_key,
                    "q": search_term,
                    "limit": 50,  # Get 50 results to choose from
                    "rating": "g"  # Keep it family friendly
                }
                
                # Make request to Giphy API
                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=params) as response:
                        if response.status != 200:
                            raise Exception(f"Giphy API returned status {response.status}")
                        
                        data = await response.json()
                        if not data["data"]:
                            raise Exception("No GIFs found")
                        
                        # Get a random GIF from the results
                        gif_data = random.choice(data["data"])
                        gif_url = gif_data["images"]["original"]["url"]
                        
                        # Update embed with the GIF
                        embed.title = "Deanna Troi"
                        embed.set_image(url=gif_url)
                        
                        await interaction.edit_original_response(embed=embed)
                        
            except Exception as e:
                logger.error("Failed to fetch GIF", exc_info=e)
                embed.color = discord.Color.red()
                embed.title = "Error"
                embed.description = f"Failed to fetch GIF: {str(e)}"
                await interaction.edit_original_response(embed=embed)
