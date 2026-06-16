"""Tracks chess tournament winners"""

import discord
from discord.ext import commands
from db.repo import RepoError
from urllib.parse import urlparse


class Winners(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.repo = bot.repo

	# Checks if a url belongs to chess.com domain, returns boolean
	def _is_chess_com_url(self, url: str) -> bool:
		try:
			parsed = urlparse(url)
			return parsed.netloc in ("www.chess.com", "chess.com")
		except Exception:
			return False

	@commands.command()
	async def help(self, ctx):
		await ctx.send("""
1. $addwinner @user <tournament_url> -> add a tournament winner entry (requires moderator role to prevent abuse)
2. $leaderboard -> returns a sorted list of tournament winners with their win count
3. $wincount @user -> returns the win count of a user
4. $stats @user -> returns all the tournament wins of a user		 
		""")
		
	@commands.command()
	@commands.has_role("moderator")
	async def addwinner(self, ctx, user: discord.Member, url):
		# Basic length validation on url
		if len(url) < 32 or len(url) > 254:
			await ctx.send("Invalid url")
			return

		# Check if url domain is chess.com		
		if not self._is_chess_com_url(url):
			await ctx.send("Invalid url")
			return

		# Send to repo for saving in database
		try:
			await self.repo.add_win(str(user.id), url)
		except RepoError:
			await ctx.send("Error - please try again later")
			return

		# Retrieve new win count and send as response
		win_count = await self.repo.get_win_count(str(user.id))
		await ctx.send(f"{user.mention} now has {win_count} wins! :balloon:")

	@commands.command()
	async def leaderboard(self, ctx):
		try:
			rows = await self.repo.fetch_leaderboard()
		except RepoError:
			await ctx.send("Error - please try again later")
			return

		# Format response
		embed = discord.Embed(
			title=":trophy: Tournament Leaderboard",
			color=discord.Color.gold()
		)

		if not rows:
			embed.description = "No wins recorded yet."
		else:
			lines = []
			for i, row in enumerate(rows, start=1):
				mention = f"<@{row['player_id']}>"
				suffix = "win" if row["won"] == 1 else "wins"
				lines.append(f"**{i}.** {mention} — **{row['won']}** {suffix}")
			embed.description = "\n".join(lines)

		embed.set_footer(text=f"Requested by {ctx.author.display_name}")
		await ctx.send(embed=embed)

	@commands.command()
	async def wincount(self, ctx, user: discord.Member):
		try:
			win_count = await self.repo.get_win_count(str(user.id))
		except RepoError:
			await ctx.send("Error - please try again later")
			return
		
		await ctx.send(f"<@{user.id}> has {win_count} wins! :star:")

	@commands.command()
	async def stats(self, ctx, user: discord.Member):
		try:
			rows = await self.repo.get_stats(str(user.id))
		except RepoError:
			await ctx.send("Error - please try again later")
			return

		win_count = len(rows)

		# Format response
		# Header
		embed = discord.Embed(color=discord.Color.magenta())
		embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
		embed.set_thumbnail(url=user.display_avatar.url)

		# Win Count
		if win_count == 0:
			embed.title = ":cry: No tournaments won yet"
			embed.description = "Don't worry - watch some gothamchess videos and you will get one in no time :muscle:"
		else:
			suffix = "Tournaments" if win_count > 1 else "Tournament"
			embed.title = f":trophy: {win_count} {suffix} Won"
			embed.description = f"{user.mention} has won **{win_count}** {suffix}"

			# Display the list of wins
			history = []
			for i, row in enumerate(rows, start=1):
				medal = {1: ":first_place:", 2: ":second_place:", 3: ":third_place:"}.get(i, ":white_small_square:")
				relative = discord.utils.format_dt(row["won_at"], style="R")
				history.append(f"{medal} [{relative}]({row['tournament_url']})")
			embed.add_field(
				name="Tournament History",
				value="\n".join(history),
				inline=False
			)

			# Display first and last win
			if win_count > 1:
				first = discord.utils.format_dt(rows[-1]["won_at"], style="d")
				latest = discord.utils.format_dt(rows[0]["won_at"], style="d")
				embed.add_field(name="First win", value=first, inline=True)
				embed.add_field(name="Latest win", value=latest, inline=True)

		embed.set_footer(text=f"Requested by {ctx.author.display_name}")
		await ctx.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Winners(bot))