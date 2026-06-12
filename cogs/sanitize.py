"""Sanitizes instagram urls
1. Remove igsh parameter to protect user privacy
2. Replace instagram.com with kkinstagram.com to enable discord embeds"""

import discord
from discord.ext import commands
import re
import time
from urllib.parse import urlparse

url_regex = r"https?://[^\s]+"
igsh_regex = r"(\?igsh=[^&\s]+)"

class Sanitize(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.max_requests = 100
		self.time_window = 300 # 5 minutes
		self.request_count = 0
		self.window_start = time.time()
		self.delete_original = True
		self.add_attribution = True

	# Checks if a url belongs to instagram domain, returns boolean
	def _is_instagram_url(self, url: str) -> bool:
		try:
			parsed = urlparse(url)
			return parsed.netloc in ("www.instagram.com", "instagram.com")

		except Exception:
			return False

	# Sanitize instagram url, returns string
	def _sanitize_instagram_url(self, url: str) -> str:
		url = url.replace("www.instagram.com", "www.kkinstagram.com") # replace domain name
		url = re.sub(igsh_regex, '', url) # remove igsh parameter
		return url
	
	# Checks if rate limit has been hit, returns boolean
	def _check_rate_limit_hit(self) -> bool:
		# Update window if time window has exceeded
		current = time.time()
		if current - self.window_start > self.time_window:
			self.request_count = 0
			self.window_start = current
		
		# Check if requests exceed limit
		if self.request_count > self.max_requests:
			return True

		self.request_count += 1
		return False


	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user: # ignore messages from bot itself
			return
			
		# Extract all instagram urls
		insta_urls = []
		for match in re.finditer(url_regex, message.content):
			url = match.group()
			if self._is_instagram_url(url):
				insta_urls.append(url)

		# If no insta urls found or hit rate limit, stop processing
		if not insta_urls or self._check_rate_limit_hit():
			return

		content = message.content
		for url in insta_urls:
			sanitized = self._sanitize_instagram_url(url)
			content = content.replace(url, sanitized)

		if self.add_attribution:
			content += f"\n\nSent by: {message.author.mention}"
		
		await message.channel.send(content)

		if self.delete_original:
			try:
				await message.delete()
			except discord.errors.Forbidden:
				print(f"Could not delete user message in #{message.channel.name} from @{message.author} - Forbidden")
			except Exception as e:
				print(f"Unexpected error in #{message.channel.name} from @{message.author} - {e}")

async def setup(bot):
	await bot.add_cog(Sanitize(bot))