"""
/help command handler
Display help information and available commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import get_main_keyboard
import logging

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help command - Show help information
    """
    help_text = """
🤖 <b>Email2Telegram Bot Help</b>

<b>📧 What is this bot?</b>
This bot allows you to create custom email addresses that forward all incoming emails directly to your Telegram chat!

<b>💡 How to use:</b>

1️⃣ <b>Get Credits</b>
   Use /credits to check your balance or purchase credits
   Each credit = 1 email address

2️⃣ <b>Create Email Address</b>
   Use /add_email to create a new email alias
   Choose from available domains

3️⃣ <b>Receive Emails</b>
   Any email sent to your address will appear here instantly!

<b>📋 Available Commands:</b>
/start - Start the bot and see your status
/credits - Check balance and buy credits
/add_email - Create a new email address
/my_emails - View all your email addresses
/help - Show this help message

<b>💰 Pricing:</b>
• 1 Email Account: 2,000 MMK
• 3 Email Accounts: 5,000 MMK
• 7 Email Accounts: 10,000 MMK

<b>Need support?</b>
Contact: @yoursupport
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    
    logger.info(f"User {update.effective_user.id} viewed help")
