"""
Discord ComfyUI Integration Package

This package provides a Discord bot that integrates with ComfyUI through n8n webhooks.
It allows users to send image generation prompts via Discord commands and have them
processed by ComfyUI workflows.

Main Components:
    - main.py: Discord bot implementation with command handling
    
Environment Variables Required:
    - DISCORD_COMFY: Discord bot token
    - N8N_WEBHOOK_URL: URL for n8n webhook that triggers ComfyUI
    - DISCORD_CHANNEL_NAME: Name of Discord channel to monitor for commands

Usage:
    Run `python main.py` to start the Discord bot.
    
Commands:
    - !help: Show available commands
    - !prompt <text>: Send a prompt to ComfyUI
    - !P <text>: Shortened version of !prompt
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Discord bot for ComfyUI integration via n8n webhooks"