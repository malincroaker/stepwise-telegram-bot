"""Select translations and map translated button labels to stable actions."""

from types import ModuleType

import content
import content_ru

CONTENT = {"en": content, "ru": content_ru}
LANGUAGE_LABELS = {"en": "English", "ru": "Русский"}
MENU_ACTIONS = ("start_guide", "download_checklist", "contact_admin", "help")
GUIDE_ACTIONS = ("back", "next", "main_menu")


def get_content(language: str = "en") -> ModuleType:
    """Use English when no supported language has been selected."""
    return CONTENT.get(language, content)


def get_action(label: str | None) -> str | None:
    """Accept either language, including labels left in an older keyboard."""
    for texts in CONTENT.values():
        for action, translated_label in texts.BUTTON_LABELS.items():
            if label == translated_label:
                return action
    return None


def button_labels(actions: tuple[str, ...]) -> list[str]:
    """Collect the translated labels needed by a Telegram text filter."""
    return [
        texts.BUTTON_LABELS[action]
        for texts in CONTENT.values()
        for action in actions
    ]
