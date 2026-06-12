"""Create bot object and load cogs"""
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db.conn import create_pool
from db.repo import WinRepository
import os

# Load database variables from environment
load_dotenv()
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")

# Function to load cogs
async def load_cogs():
	for file in os.listdir("./cogs"):
		if file.endswith(".py") and not file.startswith("__"):
			await bot.load_extension(f"cogs.{file[:-3]}")

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
	else:
		raise error

# Runs during initializing
@bot.event
async def setup_hook():
	# Create database pool
	try:
		pool = await create_pool(db_name, db_user, db_pass)
	except Exception as e:
		print("Failed to create connection pool -", e)
		exit()

	# Create repository
	repo = WinRepository(pool)

	# Attach repo to bot object
	bot.repo = repo
	bot.db_pool = pool

	# Load cogs
	await load_cogs()

# Graceful shutdown
@bot.event
async def on_close():
	await bot.db_pool.close()