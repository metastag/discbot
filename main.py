"""Entry point: starts the bot"""
import os
from dotenv import load_dotenv
from bot import bot

# Load discord token from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
	bot.run(token)