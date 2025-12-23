"""
/credits command handler
Check balance and purchase credits
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import CREDIT_PLANS
import logging

logger = logging.getLogger(__name__)


async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /credits command - Check balance and purchase credits
    """
    user = update.effective_user
    
    # TODO: Fetch actual credits from database
    current_credits = 1  # Placeholder
    
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
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    
    logger.info(f"User {user.id} checked credits")
