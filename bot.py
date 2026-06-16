"""Create bot object and load cogs"""
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db.repo import WinRepository
import os

# Load database connection string
load_dotenv()
dsn = os.getenv("DSN")
if not dsn:
	print("Could not load DSN env variable")
	exit(1)

# Function to load cogs
async def load_cogs():
	for file in os.listdir("./cogs"):
		if file.endswith(".py") and not file.startswith("__"):
			try:
				await bot.load_extension(f"cogs.{file[:-3]}")
			except Exception as e:
				print(f"Failed to load cog {file} - {e}")

# Initialize intents
intents = discord.Intents.default()
intents.message_content = True # Allow bot to read chat messages

# Initialize bot with command prefix $
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)

# Bot will print this message if it starts successfully
@bot.event
async def on_ready():
	print(f"Bot {bot.user} is ready!")

# Send proper messages to user in case of user error
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.MissingRole):
		await ctx.send("You need the moderator role to run this command")
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send("Member not found")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Missing required argument, enter $help to see a list of commands with their arguments")
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send("Invalid command, enter $help to see a list of commands")
	else:
		raise error

# Runs during initializing
@bot.event
async def setup_hook():
	# Create repository
	repo = WinRepository(dsn)

	# Attach repo to bot object
	bot.repo = repo

	# Load cogs
	await load_cogs()