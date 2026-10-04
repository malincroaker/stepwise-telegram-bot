# Stepwise

A small Telegram bot built with Python.

## Features

- English main menu shown by `/start`
- Start Guide, Download Checklist, Contact Admin, and Help buttons with placeholder replies

## Technologies

Python 3.10+, python-telegram-bot, python-dotenv.

## Configuration

Create `.env` from `.env.example` and set `BOT_TOKEN` to your Telegram bot token.

## Windows

From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe bot.py
```

## Linux

Requires Python 3.10+ with `venv` support. From the project folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python bot.py
```
