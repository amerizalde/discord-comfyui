import discord
import aiohttp

from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_COMFY")

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.channel.name == "comfyui":

            if message.content.startswith('!hello'):
                await message.channel.send('Hello!')
                
            if message.content.startswith('!prompt') or message.content.startswith('!P'):
                prompt = message.content.strip('!prompt').strip('!P')
                # send prompt to webhook via POST request AI
                webhook_url = "http://192.168.0.244:5678/webhook-test/prompt"
                
                async with aiohttp.ClientSession() as session:
                    await session.post(webhook_url, json={"prompt": prompt})
                
                
intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(DISCORD_TOKEN)
