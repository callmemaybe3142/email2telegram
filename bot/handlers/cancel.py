"""
Cancel handler
Handle cancellation for payment flow (outside conversation)
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancel pending payment (not in conversation)
    """
    if context.user_data.get('pending_payment'):
        await update.message.reply_text(
            "❌ Payment cancelled.\n\n"
            "Use /credits to try again.",
            parse_mode="HTML"
        )
        logger.info(f"User {update.effective_user.id} cancelled payment")
        context.user_data.clear()
    else:
        # No pending payment, just acknowledge
        await update.message.reply_text(
            "No active process to cancel.",
            parse_mode="HTML"
        )
