import asyncio
import asyncpg
import logging

logger = logging.getLogger(__name__)

class RepoError(Exception):
	"""Generic error raised for an error in repository layer"""
	pass

class WinRepository:
	def __init__(self, dsn: str):
		self.dsn = dsn
		self.conn = None
		self._lock = asyncio.Lock()

	# Lazy connection
	# Connect once, re-use that connnection until timeout (5mins idle), re-connect on next call
	async def _get_conn(self):
		if self.conn is None:
			self.conn = await asyncpg.connect(self.dsn, timeout=10)
		elif self.conn.is_closed():
			logger.info("NeonDB connection was closed due to timeout, reconnecting...")
			await self.conn.close()
			self.conn = await asyncpg.connect(self.dsn, timeout=10)
	
		return self.conn

	async def add_win(self, player_id: str, url: str):
		async with self._lock:
			try:
				conn = await self._get_conn()
				await conn.execute("""
					INSERT INTO wins (player_id, tournament_url)
					VALUES ($1, $2) ON CONFLICT (player_id, tournament_url) DO NOTHING
				""", player_id, url)
			except Exception as e:
				logger.exception("Error in add_win() repository function - %s", e)
				raise RepoError()

	async def fetch_leaderboard(self) -> list[asyncpg.Record]:
		async with self._lock:
			try:
				conn = await self._get_conn()
				return await conn.fetch("""
					SELECT player_id, COUNT(*) AS won FROM wins
					GROUP BY player_id ORDER BY won DESC, player_id ASC
				""")
			except Exception as e:
				logger.exception("Error in fetch_leaderboard() repository function - %s", e)
				raise RepoError()
		
	async def get_win_count(self, player_id: str) -> int | None:
		async with self._lock:
			try:
				conn = await self._get_conn()
				return await conn.fetchval("""
					SELECT COUNT(*) as won FROM wins
					WHERE player_id=$1
				""", player_id)
			except Exception as e:
				logger.exception("Error in get_win_count() repository function - %s", e)
				raise RepoError()

	async def get_stats(self, player_id: str) -> list[asyncpg.Record]:
		async with self._lock:
			try:
				conn = await self._get_conn()
				return await conn.fetch("""
					SELECT tournament_url, won_at FROM wins
					WHERE player_id=$1 ORDER BY won_at DESC
				""", player_id)
			except Exception as e:
				logger.exception("Error in get_stats() repository function - %s", e)
				raise RepoError()