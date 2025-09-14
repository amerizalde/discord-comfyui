import discord
import aiohttp

from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_COMFY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
DISCORD_CHANNEL_NAME = os.getenv("DISCORD_CHANNEL_NAME")

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.channel.name == DISCORD_CHANNEL_NAME:

            if message.content.startswith('!help'):
                await message.channel.send("""
Welcome to the ComfyUI Discord Bot! Here are the commands you can use:
- `!prompt <your prompt>` or `!P <your prompt>`: Send a prompt to ComfyUI.
- `!help`: Display this help message.""")
                
            if message.content.startswith('!prompt') or message.content.startswith('!P'):
                prompt = message.content.strip('!prompt').strip('!P')
                if prompt:
                    async with aiohttp.ClientSession() as session:
                        await session.post(N8N_WEBHOOK_URL, json={"prompt": prompt})

                
intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(DISCORD_TOKEN)
