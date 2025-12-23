"""
/add_email command handler
Create new email aliases
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def add_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_email command - Create a new email alias
    """
    user = update.effective_user
    
    # TODO: Check credits from database
    current_credits = 1  # Placeholder
    
    if current_credits <= 0:
        await update.message.reply_text(
            "❌ <b>Insufficient Credits</b>\n\n"
            "You don't have any credits to create an email address.\n"
            "Use /credits to purchase more credits.",
            parse_mode="HTML"
        )
        logger.info(f"User {user.id} tried to add email with 0 credits")
        return
    
    # TODO: Fetch available domains from database
    available_domains = ["example.com", "test.com"]  # Placeholder
    
    message = f"""
📧 <b>Create New Email Address</b>

Available Credits: <b>{current_credits}</b>

🌐 <b>Available Domains:</b>
"""
    
    for idx, domain in enumerate(available_domains, 1):
        message += f"\n{idx}. @{domain}"
    
    message += """

📝 <b>How to create:</b>
Send your desired email prefix in this format:

<code>/add_email yourname@example.com</code>

<b>Rules:</b>
• Only lowercase letters, numbers, dots, and hyphens
• Must start with a letter
• 3-30 characters long

<b>Example:</b>
<code>/add_email john.doe@example.com</code>
    """
    
    await update.message.reply_text(message, parse_mode="HTML")
    
    # Check if user provided email in the command
    if context.args:
        email_address = context.args[0].lower().strip()
        # TODO: Validate and create email
        await update.message.reply_text(
            f"⏳ Processing email creation: <code>{email_address}</code>\n"
            f"(Database integration pending)",
            parse_mode="HTML"
        )
        logger.info(f"User {user.id} requested email: {email_address}")
    else:
        logger.info(f"User {user.id} viewed add_email instructions")
