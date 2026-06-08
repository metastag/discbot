### Discord bot

Built on `discord.py`, this is a discord bot made for simple utility and fun.

#### Setup:
```bash
$ git clone https://github.com/metastag/discbot.git && cd discbot
$ python -m venv .venv
$ source .venv/bin/activate # for mac/linux
$ pip install -r requirements.txt
```

Setup `.env` with the discord token and then,

Run using:
```bash
$ python main.py
```

If the bot starts correctly, it should print `Bot GothamChess#9680 is ready!` in the terminal.

#### Features:

1. Sanitizes instagram urls - remove igsh parameter for privacy, and replace the domain name with kkinstagram to enable video player in discord