"""English text and button labels for the main menu and guide."""

WELCOME_MESSAGE = "Welcome to Stepwise! Choose an option from the main menu."

MENU_LAYOUT = (
    ("Start Guide", "Download Checklist"),
    ("Contact Admin", "Help"),
)

MENU_RESPONSES = {
    "Contact Admin": "The admin contact will be added in a later step.",
    "Help": "Choose an option from the main menu. More help will be added soon.",
}

GUIDE_LAYOUT = (
    ("Back", "Next"),
    ("Main Menu",),
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
