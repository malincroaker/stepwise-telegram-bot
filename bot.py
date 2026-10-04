import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from content import (
    CHECKLIST_CAPTION,
    CHECKLIST_UNAVAILABLE_MESSAGE,
    CONTACT_MESSAGE,
    CONTACT_DEMO_BUTTON_LABEL,
    CONTACT_DEMO_MESSAGE,
    CONTACT_DEMO_URL,
    GUIDE_COMPLETE_MESSAGE,
    GUIDE_INACTIVE_MESSAGE,
    GUIDE_LAYOUT,
    GUIDE_STEPS,
    MENU_LAYOUT,
    MAIN_MENU_MESSAGE,
    HELP_MESSAGE,
    UNKNOWN_MESSAGE,
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


def navigation_keyboard(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
) -> ReplyKeyboardMarkup:
    """Keep the active guide controls available when showing other messages."""
    if f"guide_step:{chat_id}" in context.user_data:
        return ReplyKeyboardMarkup(GUIDE_LAYOUT, resize_keyboard=True)
    return main_menu_keyboard()


async def show_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Explain the bot without changing the current guide step."""
    if update.message is not None:
        await update.message.reply_text(
            HELP_MESSAGE,
            reply_markup=navigation_keyboard(context, update.message.chat_id),
        )


async def show_guide_step(update: Update, step: int) -> None:
    """Show a guide step with its navigation buttons."""
    if update.message is not None:
        await update.message.reply_text(
            f"Step {step + 1} of {len(GUIDE_STEPS)}\n\n{GUIDE_STEPS[step]}",
            reply_markup=ReplyKeyboardMarkup(GUIDE_LAYOUT, resize_keyboard=True),
        )


async def send_checklist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Send the fixed checklist file or a helpful availability message."""
    if update.message is None:
        return
    try:
        with CHECKLIST_PATH.open("rb") as checklist:
            await update.message.reply_document(
                document=checklist,
                filename="checklist.pdf",
                caption=CHECKLIST_CAPTION,
                reply_markup=navigation_keyboard(context, update.message.chat_id),
            )
    except OSError:
        logger.warning("The checklist file could not be read.")
        await update.message.reply_text(
            CHECKLIST_UNAVAILABLE_MESSAGE,
            reply_markup=navigation_keyboard(context, update.message.chat_id),
        )


def read_admin_contact_url() -> str:
    """Accept only an explicitly configured public Telegram username link."""
    url = os.environ.get("ADMIN_CONTACT_URL", "").strip()
    if url and not re.fullmatch(r"https://t\.me/[A-Za-z][A-Za-z0-9_]{3,31}", url):
        logger.warning(
            "ADMIN_CONTACT_URL must be an HTTPS t.me username link. "
            "The demo contact will be shown."
        )
        return ""
    return url


async def show_admin_contact(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show a configured admin link or an explicitly labeled demo link."""
    if update.message is None:
        return
    url = context.bot_data.get("admin_contact_url", "")
    if url:
        text = f"{CONTACT_MESSAGE}\n{url}"
        keyboard = navigation_keyboard(context, update.message.chat_id)
    else:
        text = CONTACT_DEMO_MESSAGE
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(CONTACT_DEMO_BUTTON_LABEL, url=CONTACT_DEMO_URL)]]
        )
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
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
        await send_checklist(update, context)
        return
    if update.message.text == "Contact Admin":
        await show_admin_contact(update, context)
        return
    if update.message.text == "Help":
        await show_help(update, context)


async def guide_navigation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Move through the guide without sharing progress between users or chats."""
    if update.message is None:
        return
    action = update.message.text
    progress_key = f"guide_step:{update.message.chat_id}"
    step = context.user_data.get(progress_key)
    if action == "Main Menu" or (action == "Back" and step == 0):
        context.user_data.pop(progress_key, None)
        await update.message.reply_text(
            MAIN_MENU_MESSAGE, reply_markup=main_menu_keyboard()
        )
        return
    if action not in ("Next", "Back"):
        return
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
        step -= 1
    context.user_data[progress_key] = step
    await show_guide_step(update, step)


async def unknown_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Suggest supported actions without echoing text or changing progress."""
    if update.message is not None:
        await update.message.reply_text(
            UNKNOWN_MESSAGE,
            reply_markup=navigation_keyboard(context, update.message.chat_id),
        )


async def handle_error(
    _update: object,
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
        application.bot_data["admin_contact_url"] = read_admin_contact_url()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", show_help))
        menu_labels = [label for row in MENU_LAYOUT for label in row]
        application.add_handler(
            MessageHandler(
                filters.Text(menu_labels) & ~filters.COMMAND,
                menu_choice,
            )
        )
        guide_labels = [label for row in GUIDE_LAYOUT for label in row]
        application.add_handler(
            MessageHandler(
                filters.Text(guide_labels) & ~filters.COMMAND,
                guide_navigation,
            )
        )
        # Keep the fallback last so known commands and buttons are handled first.
        application.add_handler(
            MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, unknown_message)
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
