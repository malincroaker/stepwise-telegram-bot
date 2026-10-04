# Stepwise

Stepwise is a Telegram bot that guides users through a short process and provides a PDF checklist they can keep for later. Its interface, guide content, and messages are in English.

The included guide covers three stages of a small project: setting a goal, planning the work, and checking the result.

## Features

- **Main menu:** `/start` shows four actions through Telegram buttons.
- **Three-step guide:** Start Guide opens the first step. Next and Back move between steps; Main Menu returns to the menu.
- **Guide completion:** Next on the final step shows a completion message. The guide can be started again from the beginning.
- **Separate progress:** Each user has independent progress in each chat. Progress is held in memory and resets when the bot restarts.
- **Admin contact:** Contact Admin displays the configured Telegram contact link. When no contact is configured, an explicitly labeled demo shows an Open Demo Link button leading to `https://example.com`.
- **PDF download:** Download Checklist sends the included project checklist. If the file is unavailable, the bot responds with a short availability message.

- **Help:** `/help` and Help explain the menu, guide navigation, PDF download, and admin contact. Help preserves the current guide step.
- **Message guidance:** Unknown text and commands receive a helpful hint with the current navigation buttons, without changing guide progress.

## Menu

| Button | Action |
| --- | --- |
| Start Guide | Open the three-step guide. |
| Download Checklist | Receive the project checklist as a PDF document. |
| Contact Admin | Show the configured admin link, or preview a link button using the example website. |
| Help | Show instructions and keep the current guide step. |

## Commands

| Command | Action |
| --- | --- |
| `/start` | Return to the main menu and reset the guide in the current chat. |
| `/help` | Show instructions without resetting guide progress. |

Help and unknown-message replies retain Next, Back, and Main Menu while a guide is active. Outside a guide, they show the main menu.

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

`bot.py` starts the application and handles commands, menu actions, guide navigation, document delivery, and unknown text. `content.py` contains the English messages, button labels, and guide text. `files/checklist.pdf` is the document sent by Download Checklist.

## Setup and run

Create `.env` from `.env.example` and set `BOT_TOKEN` to your Telegram bot token. Optionally set `ADMIN_CONTACT_URL` to a public Telegram username link in the form `https://t.me/<username>`. Leave it empty to show the demo contact with a link to `https://example.com`.

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
