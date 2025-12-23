"""
/credits command handler
Display credit balance and purchase options
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from database import AsyncSessionLocal, User
from config import CREDIT_PLANS, KPAY_PHONE, KPAY_NAME
import logging

logger = logging.getLogger(__name__)


async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /credits command - Show credit balance and purchase options
    """
    user = update.effective_user
    
    async with AsyncSessionLocal() as session:
        # Fetch user from database
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            # User not registered
            await update.message.reply_text(
                "⚠️ Please use /start first to register.",
                parse_mode="HTML"
            )
            logger.warning(f"User {user.id} not found in database")
            return
        
        # Get current credits
        current_credits = db_user.credits
    
    message = f"""
💳 <b>Your Credit Balance</b>

Current Credits: <b>{current_credits}</b> email(s)

📦 <b>Available Plans:</b>

"""
    
    # Add plan details
    for plan_id, plan_info in CREDIT_PLANS.items():
        message += f"\n• <b>{plan_info['name']}</b>: {plan_info['price']} MMK"
    
    message += "\n\n💰 <b>Purchase Credits:</b>\nSelect a plan below to proceed with payment."
    
    # Create inline keyboard with plan options
    keyboard = []
    for plan_id, plan_info in CREDIT_PLANS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"🎫 {plan_info['name']} - {plan_info['price']} MMK",
                callback_data=f"buy_{plan_id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    logger.info(f"User {user.id} checked credits: {current_credits}")
