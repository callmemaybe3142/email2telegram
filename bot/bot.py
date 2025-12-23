"""
Telegram Bot Application
Runs alongside FastAPI server
"""

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from config import TELEGRAM_BOT_TOKEN
from bot.handlers import (
    start_command,
    credits_command,
    add_email_command,
    my_emails_command,
    help_command,
    handle_payment_callback,
    handle_photo,
    handle_admin_callback
)
import logging

logger = logging.getLogger(__name__)


def create_bot_application():
    """
    Create and configure the Telegram bot application
    """
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("credits", credits_command))
    application.add_handler(CommandHandler("add_email", add_email_command))
    application.add_handler(CommandHandler("my_emails", my_emails_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(
        handle_payment_callback,
        pattern="^buy_"
    ))
    application.add_handler(CallbackQueryHandler(
        handle_admin_callback,
        pattern="^(approve_|reject_)"
    ))
    
    # Message handlers
    application.add_handler(MessageHandler(
        filters.PHOTO,
        handle_photo
    ))
    
    logger.info("Telegram bot application configured")
    
    return application


async def send_email_notification(telegram_id: int, email_data: dict, bot_application):
    """
    Send email notification to user
    
    Args:
        telegram_id: User's Telegram ID
        email_data: Dictionary containing email information
        bot_application: Telegram bot application instance
    """
    try:
        message = f"""
📧 <b>New Email Received!</b>

<b>From:</b> <code>{email_data.get('from', 'Unknown')}</code>
<b>To:</b> <code>{email_data.get('to', 'Unknown')}</code>
<b>Subject:</b> {email_data.get('subject', 'No Subject')}

<b>Message:</b>
{email_data.get('body_plain', 'No content')[:500]}
{'...' if len(email_data.get('body_plain', '')) > 500 else ''}

---
📎 Attachments: {email_data.get('attachment_count', 0)}
        """
        
        await bot_application.bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )
        
        logger.info(f"Email notification sent to user {telegram_id}")
        
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
