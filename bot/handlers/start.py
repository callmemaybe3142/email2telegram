"""
/start command handler
User onboarding and welcome message
"""

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from database import AsyncSessionLocal, User
from bot.keyboards import get_main_keyboard
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command - User onboarding
    Saves new users to database or welcomes back existing users
    """
    user = update.effective_user
    
    async with AsyncSessionLocal() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if db_user:
            # Existing user - welcome back
            welcome_message = f"""
👋 <b>Welcome back, {user.first_name}!</b>

You have <b>{db_user.credits}</b> credit(s) available.

💡 <b>Quick Commands:</b>
Use the keyboard below or type:
/credits - Check balance &amp; buy credits
/add_email - Create a new email alias
/my_emails - View your email addresses
/help - Get help

Ready to manage your emails! 🚀
            """
            logger.info(f"Existing user returned: {user.id} (@{user.username})")
        else:
            # New user - create account
            new_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                credits=1  # Default 1 free credit
            )
            session.add(new_user)
            await session.commit()
            
            welcome_message = f"""
👋 <b>Welcome to Email2Telegram Service!</b>

Hello {user.first_name}! 

🎉 <b>You've received 1 FREE credit!</b>

🎯 <b>What we offer:</b>
• Custom email addresses forwarded to your Telegram
• Instant notifications when you receive emails
• Multiple email aliases support
• Secure and private

📧 <b>How it works:</b>
1. Use your free credit or purchase more with /credits
2. Create email aliases using /add_email
3. Receive emails directly in Telegram!

💡 <b>Quick Commands:</b>
Use the keyboard below or type:
/credits - Check balance &amp; buy credits
/add_email - Create a new email alias
/my_emails - View your email addresses
/help - Get help

Let's get started! 🚀
            """
            logger.info(f"New user registered: {user.id} (@{user.username}) - {user.first_name}")
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

