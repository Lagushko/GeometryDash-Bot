# Geometry Dash Bot

🎮 **Geometry Dash Bot** is a simulation-based Discord bot inspired by Geometry Dash. Players can beat levels, earn rewards, unlock icons, submit levels, climb leaderboards, and more — all inside Discord!

---

## 📁 Project Structure

```
project/
│
├── bot.py               # Bot creation and configuration
├── database.py          # Handles user, level, and global database logic
├── main.py              # Bot launch and commands registration
│
├── utils/               # Utilities for project
│   ├── __init__.py      # Initializes all utils files
│   ├── config.py        # Loads all configuration from .env
│   ├── constants.py     # Constants like emojis
│   └── functions.py     # Additional functions
│
├── modules/             # Main command logic
│   └── __init__.py      # Initializes modules
│   └── __utils__.py     # Libraries import and modules utilities
│   └── ...              # Modules with commands
│
├── data/                # SQLite databases
│   ├── users.db         # User data
│   ├── levels.db        # Saved levels
│   └── settings.db      # Global bot data
│
├── manual/              # Manual DB tools (not required for bot to run)
│   └── ...              # Admin scripts for manual data management
│
├── .env                 # Secret bot data
└── requirements.txt     # Project dependencies
```

---

## 📖 Commands

Run `!help` in Discord to see all available commands.

### Basic Commands:

* `!help`, `!link`, `!profile`, `!leaderboards`, `!visual`

### Levels:

* `!main`, `!search`, `!recent`, `!creator`

### Interaction:

* `!join`, `!quit`, `!play`, `!like`, `!dislike`

### Bonuses:

* `!map-pack`, `!daily`, `!weekly`, `!reward`

### Icon Shop:

* `!shop`, `!buy`, `!equip`

### Submissions:

* `!send`, `!sent-list`

### Admin Only:

* `!add-level`, `!add-mappack`, `!delete-user`, `!delete-level`, `!delete-sent`, `!cheats`, `!manage`

### Bot Control:

* `!update-db`, `!set-db`, `!role`, `!data`

---

## 🚀 Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file and configure it:

   ```env
   APP_ID=your_app_id
   PUBLIC_KEY=your_public_key
   TOKEN_BOT=your_bot_token
   BOT_URL=your_bot_url
   OWNER=your_discord_account_id
   ```

3. Launch the bot:

   ```bash
   python main.py
   ```

---

## 📦 Extras

* `manual/` — optional scripts for manually editing databases (not required). Launch with:
  
  ```bash
  python -m manual.script
  ```

* `data/` — SQLite databases, openable with tools like DB Browser for SQLite

---

## 👤 Author

**lagushkeee6400** — development, logic, commands, administration

## 🧱 Development

* `2800+` lines of code
* `40+` hours of work

## ✨ Socials

* [YouTube](https://www.youtube.com/@iSlimEkGD)
* [GitHub](https://github.com/Lagushko)
* [Email](https://mail.google.com/mail/?view=cm&fs=1&to=lyagushkeee@gmail.com)

---

🎮 Have fun!

---

_© Geometry Dash discord-bot 2025_