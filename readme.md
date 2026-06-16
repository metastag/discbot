### Discord bot

A Discord bot that tracks local server chess tournament winners and automatically sanitizes instagram urls

### Features

- **Chess leaderboard** - Track local chess tournament winners
- **Instagram URL sanitization** — replaces `instagram.com` → `kkinstagram.com` to trigger Discord embeds and removes the `?igsh=` tracking parameter from Instagram URLs
- **Rate limiting** — Uses a simple fixed window approach to limit requests at 100req every 5 minutes

### Future Work
- Extend rate limiting to all cogs
- Abstract db connection away from bot.py
- If adding more cogs, restructure repository layer and help command to support multiple cogs
- **Economy** - Add an economy system powered by chess matches, a way to earn, trade, buy items and bet money

## Getting started

### Prerequisites

- Python 3.10+
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

### Setup

```bash
# Clone the repo
$ git clone https://github.com/metastag/discbot.git && cd discbot

# Activate venv and install dependencies
$ python -m venv .venv
$ source .venv/bin/activate # for mac/linux
$ pip install -r requirements.txt

# Create a .env file with your bot token
$ echo "DISCORD_TOKEN=your_token_here" > .env

# Add DB_DSN to .env file as well

# Run the bot
$ docker compose up -d # starts postgres instance
$ python main.py
```

The bot will connect and print `Bot <name> is ready!` once it's online.

### Required bot permissions

In the Discord Developer Portal, enable these **Intents** for your bot:

- **Message Content Intent** — required to read message content (set in `bot.py` line 14)

For the bot to delete messages in a channel, its role needs the **Manage Messages** permission. If the bot lacks it, it logs a warning and skips the deletion.

## Caveats

- **Database connection uses lazy initialization instead of pooling** to save database cost. This means that requests sent after a 5 minute period of inactivity will get a delayed response due to cold start, after that the responses will be fast (~2 seconds)
- **Add Winner command requires moderator role** to prevent abuse by random people who can spam this command, only trusted people given the moderator role can run this command
- **Rate limiting is per bot instance**, not per guild or per user. At 100 requests per 5 minutes, a busy server can hit the cap. Increase `max_requests` or `time_window` if needed.
- **Message deletion requires permissions.** If the bot's role lacks Manage Messages in a channel, it logs `"Could not delete user message ... - Forbidden"` and leaves the original in place. The sanitized copy is still posted alongside it.
- **Sentinel errors** were not added as they are overkill for this project. The repo layer returns a `RepoError` for any error. This means that for future additions if the cog layer wants to conditionally handle a repo-level error, it will have to implement sentinel errors first.

## Adding new cogs

Drop a `.py` file into `cogs/` with a standard Discord.py cog structure and an async `setup()` function. The bot auto-discovers it on startup via `bot.py`'s `load_cogs()`.

## Configuration

All configuration is in `cogs/sanitize.py`:

| Setting | Default | Description |
|---|---|---|
| `max_requests` | `100` | Max sanitizations per time window |
| `time_window` | `300` (seconds, 5 min) | Rolling time window for rate limiting |
| `delete_original` | `True` | Whether to delete the user's original message |
| `add_attribution` | `True` | Whether to append "Sent by: @user" to the sanitized message |
| `command_prefix` | `"$"` | Set in `bot.py` line 17 |

To change defaults, edit the values directly in `cogs/sanitize.py`.

## How it works

A postgres database is used to store chess tournament wins. Then with a few simple queries we can fetch leaderboards, or user stats. check `cogs/winners.py` and `db/repo.py`

The `kkinstagram.com` domain is a community-maintained proxy that serves the same Instagram content but returns proper Open Graph metadata, which Discord uses to generate link embeds.