"""
Keyboard helper
Creates reply keyboards for the bot
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    """
    Get the main menu keyboard with common commands
    """
    keyboard = [
        [
            KeyboardButton("💳 Credits"),
            KeyboardButton("📧 Add Email")
        ],
        [
            KeyboardButton("📬 My Emails"),
            KeyboardButton("❓ Help")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Choose a command..."
    )
