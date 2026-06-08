"""Sanitizes instagram urls
1. Remove igsh parameter to protect user privacy
2. Replace instagram.com with kkinstagram.com to enable discord embeds"""

from discord.ext import commands

class Sanitize(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user: # ignore messages from bot itself
			return

		if "instagram.com" in message.content:
			link = message.content.replace("instagram.", "kkinstagram.")
			if "?igsh" in link:
				link = link.split("?igsh")[0]
			await message.channel.send(link)

		# Allow regular commands to run
		await self.bot.process_commands(message)
	

async def setup(bot):
	await bot.add_cog(Sanitize(bot))