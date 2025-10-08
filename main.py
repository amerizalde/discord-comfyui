"""
Discord ComfyUI Bot

This module implements a Discord bot that interfaces with ComfyUI through n8n webhooks.
The bot listens for commands in a specified Discord channel and forwards prompts
to ComfyUI for image generation.

Dependencies:
    - discord.py: Discord API wrapper for Python
    - aiohttp: Asynchronous HTTP client/server framework
    - python-dotenv: Load environment variables from .env file
"""

import discord
import aiohttp

from dotenv import load_dotenv
import os

from discord.ext import commands
from discord import app_commands


# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_COMFY")  # Discord bot token
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")  # n8n webhook URL for ComfyUI integration
DISCORD_CHANNEL_NAME = os.getenv("DISCORD_CHANNEL_NAME")  # Target Discord channel name
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", 0))  # Discord Guild ID for command syncing


class Client(commands.Bot):
    """
    Custom Discord client for ComfyUI integration.
    
    This class extends discord.Client to handle Discord events and commands
    for interfacing with ComfyUI through n8n webhooks.
    """
    
    async def on_ready(self):
        """
        Event handler called when the bot has successfully connected to Discord.
        
        Prints a confirmation message with the bot's username.
        """
        print(f'Logged in as {self.user}')
        
        try:
            guild = discord.Object(id=DISCORD_GUILD_ID)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild {guild.id}')
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_message(self, message):
        """
        Event handler for processing incoming Discord messages.
        
        Processes commands in the specified channel and forwards prompts
        to ComfyUI via n8n webhook.
        
        Args:
            message (discord.Message): The Discord message object containing
                                     user input, channel info, and metadata.
        """
        # Ignore messages from the bot itself to prevent infinite loops
        if message.author == self.user:
            return
        
        # Only process messages from the configured channel
        if message.channel.name == DISCORD_CHANNEL_NAME:

            # Handle help command - display available bot commands
            if message.content.startswith('!help'):
                await message.channel.send("""
Welcome to the ComfyUI Discord Bot! Here are the commands you can use:
- `!prompt <your prompt>` or `!P <your prompt>`: Send a prompt to ComfyUI.
- `!help`: Display this help message.""")
                
            # Handle prompt commands - send user prompts to ComfyUI
            if message.content.startswith('!prompt') or message.content.startswith('!P'):
                # Extract the prompt text by removing the command prefix
                prompt = message.content.replace('!prompt', '').replace('!P', '').strip()
                
                # Only send non-empty prompts to avoid wasting API calls
                if prompt:
                    try:
                        # Send prompt to n8n webhook for ComfyUI processing
                        async with aiohttp.ClientSession() as session:
                            await session.post(N8N_WEBHOOK_URL, json={"prompt": prompt})
                    except Exception as e:
                        # Log error if webhook request fails
                        print(f"Error sending prompt to webhook: {e}")
                        await message.channel.send("Sorry, there was an error processing your prompt.")


def main():
    """
    Main function to initialize and run the Discord bot.
    
    Sets up the necessary Discord intents, creates the client instance,
    and starts the bot with the provided token.
    """
    # Configure Discord intents - permissions for what events the bot can receive
    intents = discord.Intents.default()
    intents.message_content = True  # Required to read message content for commands
    
    # Create and run the Discord client
    client = Client(command_prefix='!', intents=intents)
    
    guild = discord.Object(id=DISCORD_GUILD_ID)

    @client.tree.command(name="help", description="Show available commands", guild=guild)
    async def help_command(interaction: discord.Interaction):
        """
        Slash command to display available bot commands.
        
        Args:
            interaction (discord.Interaction): The interaction object representing
                                               the slash command invocation.
        """
        await interaction.response.send_message("""
Welcome to the ComfyUI Discord Bot! Here are the commands you can use:
- `/prompt <your prompt>`: Send a prompt to ComfyUI.
- `/help`: Display this help message.
""")
        
        
    @client.tree.command(name="prompt", description="Send a prompt to ComfyUI", guild=guild)
    @app_commands.describe(prompt="The prompt text to send to ComfyUI")
    async def prompt_command(interaction: discord.Interaction, prompt: str):
        """
        Slash command to send a prompt to ComfyUI via n8n webhook.
        
        Args:
            interaction (discord.Interaction): The interaction object representing
                                               the slash command invocation.
            prompt (str): The prompt text provided by the user.
        """
        if prompt:
            try:
                # Send prompt to n8n webhook for ComfyUI processing
                async with aiohttp.ClientSession() as session:
                    await session.post(N8N_WEBHOOK_URL, json={"prompt": prompt})
                await interaction.response.send_message("Your prompt has been sent to ComfyUI!")
            except Exception as e:
                # Log error if webhook request fails
                print(f"Error sending prompt to webhook: {e}")
                await interaction.response.send_message("Sorry, there was an error processing your prompt.")
        else:
            await interaction.response.send_message("Please provide a valid prompt.")
            
    
    try:
        # Start the bot - this blocks until the bot is stopped
        client.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Error starting Discord bot: {e}")


# Entry point - run the bot when script is executed directly
if __name__ == "__main__":
    main()
