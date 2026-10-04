import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from content import MENU_LAYOUT, MENU_RESPONSES, WELCOME_MESSAGE


logger = logging.getLogger(__name__)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Reply to the /start command."""
    if update.message is not None:
        await update.message.reply_text(
            WELCOME_MESSAGE, reply_markup=main_menu_keyboard()
        )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create the main menu shown below the message input."""
    return ReplyKeyboardMarkup(MENU_LAYOUT, resize_keyboard=True)


async def menu_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Reply with the placeholder for a recognized menu button."""
    if update.message is None:
        return
    response = MENU_RESPONSES.get(update.message.text)
    if response is not None:
        await update.message.reply_text(response, reply_markup=main_menu_keyboard())


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
        menu_pattern = re.compile(
            r"\A(?:" + "|".join(re.escape(label) for label in MENU_RESPONSES) + r")\Z"
        )
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.Regex(menu_pattern),
                menu_choice,
            )
        )
        application.add_error_handler(handle_error)
        application.run_polling()
    except TelegramError:
        raise SystemExit(
            "The bot could not run. Check your token, network connection, "
            "and that no other instance is running."
        ) from None


if __name__ == "__main__":
    main()
