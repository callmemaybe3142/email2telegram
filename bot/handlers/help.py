"""
/help command handler
Show help information and available commands
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help command - Show help information
    """
    user = update.effective_user
    
    help_text = """
📚 <b>Help &amp; Commands</b>

<b>Available Commands:</b>

/start - Start the bot and see welcome message
/credits - Check your credit balance and buy more
/add_email - Create a new email address
/my_emails - View all your email addresses
/help - Show this help message

<b>How Credits Work:</b>
• Each credit = 1 email account
• Credits are used when you create an email
• Purchase credits via KPay payment

<b>Pricing:</b>
• 1 Email Account - 2000 MMK
• 3 Email Accounts - 5000 MMK
• 7 Email Accounts - 10000 MMK

<b>Payment Process:</b>
1. Use /credits and select a plan
2. Transfer to KPay number shown
3. Upload payment screenshot
4. Wait for admin approval
5. Credits added automatically

<b>Need Support?</b>
Contact: @yoursupport (update this)

<b>Privacy:</b>
• Your emails are private and secure
• We only store necessary metadata
• Emails are forwarded, not stored permanently
    """
    
    await update.message.reply_text(help_text, parse_mode="HTML")
    logger.info(f"User {user.id} viewed help")
