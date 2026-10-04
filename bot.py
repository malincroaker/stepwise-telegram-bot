import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from localization import (
    GUIDE_ACTIONS,
    LANGUAGE_LABELS,
    MENU_ACTIONS,
    button_labels,
    get_action,
    get_content,
)


logger = logging.getLogger(__name__)
FILES_DIRECTORY = Path(__file__).resolve().parent / "files"


def main_menu_keyboard(context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """Create the main menu shown below the message input."""
    texts = get_content(context.user_data.get("language", "en"))
    return ReplyKeyboardMarkup(texts.MENU_LAYOUT, resize_keyboard=True)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Reset this user's guide in this chat and show the main menu."""
    texts = get_content(context.user_data.get("language", "en"))
    if update.message is not None:
        context.user_data.pop(f"guide_step:{update.message.chat_id}", None)
        await update.message.reply_text(
            texts.WELCOME_MESSAGE, reply_markup=main_menu_keyboard(context)
        )
        if "language" not in context.user_data:
            await show_language_menu(update, context)


def navigation_keyboard(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
) -> ReplyKeyboardMarkup:
    """Keep the active guide controls available when showing other messages."""
    texts = get_content(context.user_data.get("language", "en"))
    if f"guide_step:{chat_id}" in context.user_data:
        return ReplyKeyboardMarkup(texts.GUIDE_LAYOUT, resize_keyboard=True)
    return main_menu_keyboard(context)


async def show_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Explain the bot without changing the current guide step."""
    texts = get_content(context.user_data.get("language", "en"))
    if update.message is not None:
        await update.message.reply_text(
            texts.HELP_MESSAGE,
            reply_markup=navigation_keyboard(context, update.message.chat_id),
        )


async def show_guide_step(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    step: int,
) -> None:
    """Show the current guide step in the selected language."""
    texts = get_content(context.user_data.get("language", "en"))
    await message.reply_text(
        texts.GUIDE_STEP_TEMPLATE.format(
            step=step + 1, total=len(texts.GUIDE_STEPS), text=texts.GUIDE_STEPS[step]
        ),
        reply_markup=ReplyKeyboardMarkup(texts.GUIDE_LAYOUT, resize_keyboard=True),
    )


async def send_checklist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Send the fixed checklist file or a helpful availability message."""
    texts = get_content(context.user_data.get("language", "en"))
    if update.message is None:
        return
    try:
        with (FILES_DIRECTORY / texts.CHECKLIST_FILENAME).open("rb") as checklist:
            await update.message.reply_document(
                document=checklist,
                filename=texts.CHECKLIST_FILENAME,
                caption=texts.CHECKLIST_CAPTION,
                reply_markup=navigation_keyboard(context, update.message.chat_id),
            )
    except OSError:
        logger.warning("The checklist file could not be read.")
        await update.message.reply_text(
            texts.CHECKLIST_UNAVAILABLE_MESSAGE,
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
    texts = get_content(context.user_data.get("language", "en"))
    if update.message is None:
        return
    url = context.bot_data.get("admin_contact_url", "")
    if url:
        text = f"{texts.CONTACT_MESSAGE}\n{url}"
        keyboard = navigation_keyboard(context, update.message.chat_id)
    else:
        text = texts.CONTACT_DEMO_MESSAGE
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(texts.CONTACT_DEMO_BUTTON_LABEL, url=texts.CONTACT_DEMO_URL)]]
        )
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


async def show_language_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Offer a language choice without resetting guide progress."""
    if update.message is None:
        return
    texts = get_content(context.user_data.get("language", "en"))
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"language:{code}")
         for code, label in LANGUAGE_LABELS.items()]
    ])
    await update.message.reply_text(texts.LANGUAGE_PROMPT, reply_markup=keyboard)


async def select_language(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Remember the user's choice and refresh their current guide or menu."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    if query.data not in ("language:en", "language:ru"):
        return
    if not isinstance(query.message, Message):
        return
    language = query.data.split(":", 1)[1]
    context.user_data["language"] = language
    texts = get_content(language)
    await query.edit_message_text(texts.LANGUAGE_SELECTED_MESSAGE)
    step = context.user_data.get(f"guide_step:{query.message.chat_id}")
    if step is not None:
        await show_guide_step(query.message, context, step)
    else:
        await query.message.reply_text(
            texts.MAIN_MENU_MESSAGE, reply_markup=main_menu_keyboard(context)
        )


async def menu_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start the guide or reply to another recognized menu button."""
    if update.message is None:
        return
    action = get_action(update.message.text)
    progress_key = f"guide_step:{update.message.chat_id}"
    if action == "start_guide":
        context.user_data[progress_key] = 0
        await show_guide_step(update.message, context, 0)
        return
    if action == "download_checklist":
        await send_checklist(update, context)
        return
    if action == "contact_admin":
        await show_admin_contact(update, context)
        return
    if action == "help":
        await show_help(update, context)


async def guide_navigation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Move through the guide without sharing progress between users or chats."""
    texts = get_content(context.user_data.get("language", "en"))
    if update.message is None:
        return
    action = get_action(update.message.text)
    progress_key = f"guide_step:{update.message.chat_id}"
    step = context.user_data.get(progress_key)
    if action == "main_menu" or (action == "back" and step == 0):
        context.user_data.pop(progress_key, None)
        await update.message.reply_text(
            texts.MAIN_MENU_MESSAGE, reply_markup=main_menu_keyboard(context)
        )
        return
    if action not in ("next", "back"):
        return
    if step is None:
        await update.message.reply_text(
            texts.GUIDE_INACTIVE_MESSAGE, reply_markup=main_menu_keyboard(context)
        )
        return
    if action == "next":
        if step == len(texts.GUIDE_STEPS) - 1:
            context.user_data.pop(progress_key, None)
            await update.message.reply_text(
                texts.GUIDE_COMPLETE_MESSAGE, reply_markup=main_menu_keyboard(context)
            )
            return
        step += 1
    else:
        step -= 1
    context.user_data[progress_key] = step
    await show_guide_step(update.message, context, step)


async def unknown_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Suggest supported actions without echoing text or changing progress."""
    texts = get_content(context.user_data.get("language", "en"))
    if update.message is not None:
        await update.message.reply_text(
            texts.UNKNOWN_MESSAGE,
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
        application.add_handler(CommandHandler("language", show_language_menu))
        application.add_handler(
            CallbackQueryHandler(select_language, pattern=r"\Alanguage:(?:en|ru)\Z")
        )
        menu_labels = button_labels(MENU_ACTIONS)
        application.add_handler(
            MessageHandler(
                filters.Text(menu_labels) & ~filters.COMMAND,
                menu_choice,
            )
        )
        guide_labels = button_labels(GUIDE_ACTIONS)
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
