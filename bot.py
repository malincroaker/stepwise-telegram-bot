import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from content import (
    CHECKLIST_CAPTION,
    CHECKLIST_UNAVAILABLE_MESSAGE,
    GUIDE_COMPLETE_MESSAGE,
    GUIDE_INACTIVE_MESSAGE,
    GUIDE_LAYOUT,
    GUIDE_STEPS,
    MENU_LAYOUT,
    MENU_RESPONSES,
    WELCOME_MESSAGE,
)


logger = logging.getLogger(__name__)
CHECKLIST_PATH = Path(__file__).resolve().parent / "files" / "checklist.pdf"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create the main menu shown below the message input."""
    return ReplyKeyboardMarkup(MENU_LAYOUT, resize_keyboard=True)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Reset this user's guide in this chat and show the main menu."""
    if update.message is not None:
        context.user_data.pop(f"guide_step:{update.message.chat_id}", None)
        await update.message.reply_text(
            WELCOME_MESSAGE, reply_markup=main_menu_keyboard()
        )


async def show_guide_step(update: Update, step: int) -> None:
    """Show a guide step with its navigation buttons."""
    if update.message is not None:
        await update.message.reply_text(
            f"Step {step + 1} of {len(GUIDE_STEPS)}\n\n{GUIDE_STEPS[step]}",
            reply_markup=ReplyKeyboardMarkup(GUIDE_LAYOUT, resize_keyboard=True),
        )


async def send_checklist(update: Update) -> None:
    """Send the fixed checklist file or a helpful availability message."""
    if update.message is None:
        return
    try:
        with CHECKLIST_PATH.open("rb") as checklist:
            await update.message.reply_document(
                document=checklist,
                filename="checklist.pdf",
                caption=CHECKLIST_CAPTION,
                reply_markup=main_menu_keyboard(),
            )
    except OSError:
        logger.warning("The checklist file could not be read.")
        await update.message.reply_text(
            CHECKLIST_UNAVAILABLE_MESSAGE, reply_markup=main_menu_keyboard()
        )


async def menu_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start the guide or reply to another recognized menu button."""
    if update.message is None:
        return
    progress_key = f"guide_step:{update.message.chat_id}"
    if update.message.text == "Start Guide":
        context.user_data[progress_key] = 0
        await show_guide_step(update, 0)
        return
    if update.message.text == "Download Checklist":
        context.user_data.pop(progress_key, None)
        await send_checklist(update)
        return
    response = MENU_RESPONSES.get(update.message.text)
    if response is not None:
        context.user_data.pop(progress_key, None)
        await update.message.reply_text(response, reply_markup=main_menu_keyboard())


async def guide_navigation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Move through the guide without sharing progress between users or chats."""
    if update.message is None:
        return
    action = update.message.text
    if action == "Main Menu":
        await start(update, context)
        return
    if action not in ("Next", "Back"):
        return
    progress_key = f"guide_step:{update.message.chat_id}"
    step = context.user_data.get(progress_key)
    if step is None:
        await update.message.reply_text(
            GUIDE_INACTIVE_MESSAGE, reply_markup=main_menu_keyboard()
        )
        return
    if action == "Next":
        if step == len(GUIDE_STEPS) - 1:
            context.user_data.pop(progress_key, None)
            await update.message.reply_text(
                GUIDE_COMPLETE_MESSAGE, reply_markup=main_menu_keyboard()
            )
            return
        step += 1
    else:
        step = max(0, step - 1)
    context.user_data[progress_key] = step
    await show_guide_step(update, step)


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
        menu_labels = [label for row in MENU_LAYOUT for label in row]
        menu_pattern = re.compile(
            r"\A(?:" + "|".join(re.escape(label) for label in menu_labels) + r")\Z"
        )
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.Regex(menu_pattern),
                menu_choice,
            )
        )
        guide_labels = [label for row in GUIDE_LAYOUT for label in row]
        guide_pattern = re.compile(
            r"\A(?:" + "|".join(re.escape(label) for label in guide_labels) + r")\Z"
        )
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.Regex(guide_pattern),
                guide_navigation,
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
