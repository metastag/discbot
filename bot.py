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

if not db_name:
	print("Could not load DB_NAME env variable")
	exit(1)
elif not db_user:
	print("Could not load DB_USER env variable")
	exit(1)
elif not db_pass:
	print("Could not lod DB_PASSWORD env variable")
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
		exit(1)

	# Create repository
	repo = WinRepository(pool)

	# Attach repo to bot object
	bot.repo = repo
	bot.db_pool = pool

	# Load cogs
	await load_cogs()

# Graceful shutdown
original_close = bot.close
async def graceful_shutdown():
	print("Closing database pool and exiting...")
	await bot.db_pool.close()
	await original_close()

bot.close = graceful_shutdown