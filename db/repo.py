import logging

logger = logging.getLogger(__name__)

class RepoError(Exception):
	"""Generic error raised for an error in repository layer"""
	pass

class WinRepository:
	def __init__(self, pool):
		self.pool = pool

	async def add_win(self, player_id: str, url: str):
		try:
			async with self.pool.acquire() as conn:
				await conn.execute("""
					INSERT INTO wins (player_id, tournament_url)
					VALUES ($1, $2)
				""", player_id, url)
		except Exception as e:
			logger.error("Error in add_win() repository function - %s", e)
			raise RepoError()

	async def fetch_leaderboard(self):
		try:
			async with self.pool.acquire() as conn:
				rows = await conn.fetch("""
					SELECT player_id, COUNT(*) AS won FROM wins
					GROUP BY player_id ORDER BY won DESC, player_id ASC
				""")
				return rows
		except Exception as e:
			logger.error("Error in fetch_leaderboard() repository function - %s", e)
			raise RepoError()
		
	async def get_win_count(self, player_id: str):
		try:
			async with self.pool.acquire() as conn:
				return await conn.fetchval("""
					SELECT COUNT(*) as won FROM wins
					WHERE player_id=$1
				""", player_id)
		except Exception as e:
			logger.error("Error in get_win_count() repository function - %s", e)
			raise RepoError()

	async def get_stats(self, player_id: str):
		try:
			async with self.pool.acquire() as conn:
				rows = await conn.fetch("""
					SELECT tournament_url, won_at FROM wins
					WHERE player_id=$1 ORDER BY won_at DESC
				""", player_id)
				return rows
		except Exception as e:
			logger.error("Error in get_stats() repository function - %s", e)
			raise RepoError()