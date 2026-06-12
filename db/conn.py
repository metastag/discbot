import asyncpg

# Create a connection pool to the database
async def create_pool(db_name: str, db_user: str, db_pass: str) -> asyncpg.Pool:
	return await asyncpg.create_pool(
		host="localhost",
		port=5432,
		database=db_name,
		user=db_user,
		password=db_pass
	)