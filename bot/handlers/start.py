"""
/start command handler
User onboarding and welcome message
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command - User onboarding
    """
    user = update.effective_user
    
    welcome_message = f"""
👋 <b>Welcome to Email2Telegram Service!</b>

Hello {user.first_name}! 

🎯 <b>What we offer:</b>
• Custom email addresses forwarded to your Telegram
• Instant notifications when you receive emails
• Multiple email aliases support
• Secure and private

📧 <b>How it works:</b>
1. Purchase credits using /credits
2. Create email aliases using /add_email
3. Receive emails directly in Telegram!

💡 <b>Quick Commands:</b>
/credits - Check balance &amp; buy credits
/add_email - Create a new email alias
/my_emails - View your email addresses
/help - Get help

Let's get started! 🚀
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="HTML"
    )
    
    # TODO: Save user to database
    logger.info(f"New user started bot: {user.id} (@{user.username})")
