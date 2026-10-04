"""English text and button labels for the main menu and guide."""

WELCOME_MESSAGE = "Welcome to Stepwise! Choose an option from the main menu."
MAIN_MENU_MESSAGE = "Main menu. Choose an option below."

BUTTON_LABELS = {
    "start_guide": "Start Guide",
    "download_checklist": "Download Checklist",
    "contact_admin": "Contact Admin",
    "help": "Help",
    "back": "Back",
    "next": "Next",
    "main_menu": "Main Menu",
}
MENU_LAYOUT = (
    (BUTTON_LABELS["start_guide"], BUTTON_LABELS["download_checklist"]),
    (BUTTON_LABELS["contact_admin"], BUTTON_LABELS["help"]),
)

HELP_MESSAGE = (
    "How to use Stepwise\n\n"
    "Start Guide: follow a three-step guide. Use Next and Back to move between "
    "steps, or Main Menu to leave the guide. Back on the first step returns to "
    "the main menu. Next on the final step completes the guide.\n\n"
    "Download Checklist: get the project checklist as a PDF in your chosen language.\n\n"
    "Contact Admin: view the configured admin link. If no contact is configured, "
    "Open Demo Link previews an example website.\n\n"
    "Help or /help: show these instructions.\n"
    "/language: choose English or Russian.\n\n"
    "Help, Download Checklist, Contact Admin, and language changes keep your guide progress.\n"
    "/start: return to the main menu and reset your guide progress."
)

UNKNOWN_MESSAGE = (
    "I didn't recognize that message or command. Use the buttons below, "
    "/help for instructions, or /start to return to the main menu."
)

GUIDE_LAYOUT = (
    (BUTTON_LABELS["back"], BUTTON_LABELS["next"]),
    (BUTTON_LABELS["main_menu"],),
)

GUIDE_STEPS = (
    "Set your goal\nChoose one small result you want to achieve. "
    "Write down what a successful result will look like.",
    "Plan your work\nBreak the task into small actions. "
    "Start with the simplest action and complete one action at a time.",
    "Check your result\nCompare your work with your original goal. "
    "Fix any issues and write a short explanation of what you completed.",
)

GUIDE_COMPLETE_MESSAGE = "Guide complete! You can start again or choose another menu option."
GUIDE_INACTIVE_MESSAGE = "Choose Start Guide from the main menu to begin."

CHECKLIST_CAPTION = "Here is your project checklist."
CHECKLIST_UNAVAILABLE_MESSAGE = (
    "The checklist is temporarily unavailable. Please try again later."
)

CONTACT_MESSAGE = "You can contact the admin here:"
CONTACT_DEMO_MESSAGE = (
    "This is a demo contact. Use the button below to preview opening a link. "
    "It opens an example website and does not contact an administrator."
)
CONTACT_DEMO_BUTTON_LABEL = "Open Demo Link"
CONTACT_DEMO_URL = "https://example.com"

GUIDE_STEP_TEMPLATE = "Step {step} of {total}\n\n{text}"
CHECKLIST_FILENAME = "checklist.pdf"
LANGUAGE_PROMPT = "Choose your language:"
LANGUAGE_SELECTED_MESSAGE = "Language set to English."
