"""Create bot object and load cogs"""
import discord
from discord.ext import commands
import os

# Function to load cogs
async def load_cogs():
	for file in os.listdir("./cogs"):
		if file.endswith(".py") and not file.startswith("__"):
			await bot.load_extension(f"cogs.{file[:-3]}")

# Initialize intents
intents = discord.Intents.default()
intents.message_content = True # Allow bot to read chat messages

# Initialize bot with command prefix $
bot = commands.Bot(command_prefix="$", intents=intents)

# Bot will print this message if it starts successfully
@bot.event
async def on_ready():
	print(f"Bot {bot.user} is ready!")

# Runs during initializing: load cogs
@bot.event
async def setup_hook():
	await load_cogs()