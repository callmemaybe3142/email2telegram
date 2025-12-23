"""
/my_emails command handler
List all user's email addresses
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def my_emails_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /my_emails command - List all user's email addresses
    """
    user = update.effective_user
    
    # TODO: Fetch emails from database
    user_emails = []  # Placeholder
    
    if not user_emails:
        message = """
📭 <b>Your Email Addresses</b>

You don't have any email addresses yet.

Use /add_email to create your first email address!
        """
    else:
        message = "📬 <b>Your Email Addresses</b>\n\n"
        for idx, email in enumerate(user_emails, 1):
            message += f"{idx}. <code>{email['address']}</code>\n"
            message += f"   Created: {email['created_at']}\n"
            message += f"   Domain: {email['domain']}\n\n"
    
    await update.message.reply_text(message, parse_mode="HTML")
    logger.info(f"User {user.id} viewed their emails")
