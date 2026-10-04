# Stepwise

Stepwise is a Telegram bot that guides users through a short process and provides a PDF checklist they can keep for later. Its interface, guide content, and messages are in English.

The included guide covers three stages of a small project: setting a goal, planning the work, and checking the result.

## Features

- **Main menu:** `/start` shows four actions through Telegram buttons.
- **Three-step guide:** Start Guide opens the first step. Next and Back move between steps; Main Menu returns to the menu.
- **Guide completion:** Next on the final step shows a completion message. The guide can be started again from the beginning.
- **Separate progress:** Each user has independent progress in each chat. Progress is held in memory and resets when the bot restarts.
- **PDF download:** Download Checklist sends the included project checklist. If the file is unavailable, the bot responds with a short availability message.

Contact Admin and Help currently return placeholder messages.

## Menu

| Button | Action |
| --- | --- |
| Start Guide | Open the three-step guide. |
| Download Checklist | Receive the project checklist as a PDF document. |
| Contact Admin | Show the current contact placeholder. |
| Help | Show the current help placeholder. |

## Technologies

- Python 3.10 or newer
- python-telegram-bot 22.8 for Telegram messages and handlers
- python-dotenv for local configuration

Dependencies are pinned in `requirements.txt`. The bot receives updates using polling.

## Project structure

```text
stepwise-telegram-bot/
├── bot.py
├── content.py
├── files/
│   └── checklist.pdf
├── requirements.txt
├── .env.example
├── .gitignore
├── .gitattributes
└── README.md
```

`bot.py` starts the application and handles menu actions, guide navigation, and document delivery. `content.py` contains the English messages, button labels, and guide text. `files/checklist.pdf` is the document sent by Download Checklist.

## Setup and run

Create `.env` from `.env.example` and set `BOT_TOKEN` to your Telegram bot token.

### Windows

Open PowerShell in the project folder, create a virtual environment, and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the bot:

```powershell
.\.venv\Scripts\python.exe bot.py
```

### Linux

Requires Python 3.10+ with `venv` support. On Ubuntu or Debian, `python3-venv` provides virtual environment support.

From the project folder, create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Start the bot:

```bash
.venv/bin/python bot.py
```

The bot runs in the foreground. Press `Ctrl+C` in the terminal to stop it.

## Content customization

Change `GUIDE_STEPS` in `content.py` to replace the sample guide. Other English messages and menu labels are defined in the same file. Button labels used for routing must also match their corresponding actions in `bot.py`.

Replace `files/checklist.pdf` to change the downloadable document while keeping the same filename.
