import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes


logger = logging.getLogger(__name__)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Reply to the /start command."""
    if update.message is not None:
        await update.message.reply_text("Hello! The bot is running.")


async def handle_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Report the error type without exposing messages, URLs, or tokens."""
    logger.error("A Telegram update failed (%s).", type(context.error).__name__)


def main() -> None:
    load_dotenv(
        dotenv_path=Path(__file__).resolve().with_name(".env"),
        encoding="utf-8-sig",
        interpolate=False,
    )
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token or token == "replace_with_your_bot_token":
        raise SystemExit(
            "Set BOT_TOKEN in the project's .env file or environment before starting."
        )

    logging.basicConfig(level=logging.WARNING)
    # HTTP request URLs include the bot token; do not enable verbose HTTP logs.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    try:
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_error_handler(handle_error)
        application.run_polling()
    except TelegramError:
        raise SystemExit(
            "The bot could not run. Check your token, network connection, "
            "and that no other instance is running."
        ) from None


if __name__ == "__main__":
    main()
