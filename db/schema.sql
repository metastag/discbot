CREATE TABLE wins (
	id SERIAL PRIMARY KEY,
	player_id VARCHAR(20) NOT NULL,
	tournament_url VARCHAR(255) NOT NULL,
	won_at TIMESTAMPTZ DEFAULT NOW(),
	-- Prevent duplicate win entries
	CONSTRAINT unique_win UNIQUE (player_id, tournament_url)
);

CREATE INDEX idx_wins_player ON wins (player_id);