# Geometry Dash Bot

🎮 **Geometry Dash Bot** is a simulation-based Discord bot inspired by Geometry Dash. Players can beat levels, earn rewards, unlock icons, submit levels, climb leaderboards, and more — all inside Discord!

---

## 📁 Project Structure

```
project/
│
├── bot.py               # Bot creation and configuration
├── database.py          # Handles user, level, and global database logic
├── config.py            # Bot configuration from .env
├── utils.py             # Utilities and constants
├── main.py              # Bot launch and commands registration
│
├── modules/             # Main command logic
│   └── __init__.py      # DB loading, permissions, visuals, global functions
│   └── ...              # Modules with commands
│
├── data/                # SQLite databases:
│   ├── users.db         # User data
│   ├── levels.db        # Saved levels
│   └── settings.db      # Global bot data
│
├── helpers/             # Manual DB tools (not required for bot to run)
│   └── ...              # Admin scripts for manual data management
│
├── .env                 # Secret bot data
└── requirements.txt     # Project dependencies
```

---

## ⚙️ Components

### `main.py`

Registers commands, and sets up the Discord client.

### `database.py`

Includes classes:

* `UserDatabase` — manages player data
* `LevelDatabase` — manages stored levels
* `BotDatabase` — manages global data (roles, settings, etc.)

### `modules/__init__.py`

* Loads modules, databases, and config
* Contains utility functions:

  * `permission(level)` — checks if a user has a specific access level (e.g., helper, admin)
  * `get_difficulty_visual(user_id, difficulty)` — returns emoji for level difficulty based on player's visual settings
  * `get_search_difficulties(user_id, name)` — filters level search results by difficulty and player settings

---

## 📖 Commands

Run `!help` in Discord to see all available commands.

### Basic Commands:

* `!help`, `!profile`, `!leaderboards`, `!main`
* `!visual`, `!search`, `!recent`, `!creator`

### Interaction:

* `!join`, `!quit`, `!play`, `!like`, `!dislike`

### Bonuses:

* `!daily`, `!weekly`, `!reward`

### Icon Shop:

* `!shop`, `!buy`, `!equip`

### Submissions:

* `!send`, `!sent-list`

### Admin Only:

* `!add-level`, `!delete-user`, `!delete-level`, `!cheats`, `!manage`

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
   OWNER=your_discord_uid
   ```

3. Launch the bot:

   ```bash
   python main.py
   ```

---

## 📦 Extras

* `helpers/` — optional scripts for manually editing databases (not required) (launch with python -m helpers.script)
* `data/` — SQLite databases, openable with tools like DB Browser for SQLite

---

## 👤 Author

**lyagushkeee6400** — development, logic, commands, administration

---

🕹️ Ready to play? Just type:

```
!play <id>
```

🎮 Have fun!
