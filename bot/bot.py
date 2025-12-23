"""
Telegram Bot Application
Runs alongside FastAPI server
"""

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from config import TELEGRAM_BOT_TOKEN
from bot.handlers import (
    start_command,
    credits_command,
    add_email_command,
    handle_email_input,
    cancel_email_creation,
    WAITING_FOR_EMAIL,
    my_emails_command,
    help_command,
    handle_payment_callback,
    handle_photo,
    handle_admin_callback,
    cancel_payment
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
    application.add_handler(CommandHandler("my_emails", my_emails_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Conversation handler for /add_email
    add_email_conv = ConversationHandler(
        entry_points=[CommandHandler("add_email", add_email_command)],
        states={
            WAITING_FOR_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email_input)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_email_creation)],
        per_user=True,  # Track conversation state per user
        per_chat=True,
        allow_reentry=True  # Allow user to start /add_email again after cancel
    )
    application.add_handler(add_email_conv)
    
    # Cancel handler for payment (outside conversation) - must come AFTER conversation handler
    application.add_handler(CommandHandler("cancel", cancel_payment))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(
        handle_payment_callback,
        pattern="^buy_"
    ))
    
    application.add_handler(CallbackQueryHandler(
        handle_admin_callback,
        pattern="^(approve|reject)_"
    ))
    
    # Photo handler for payment receipts
    application.add_handler(MessageHandler(
        filters.PHOTO,
        handle_photo
    ))
    
    logger.info("Telegram bot application configured")
    
    return application


async def send_email_notification(telegram_id: int, email_data: dict, bot_application):
    """
    Send email notification to user with attachments and full content
    
    Args:
        telegram_id: User's Telegram ID
        email_data: Dictionary containing email information
        bot_application: Telegram bot application instance
    """
    try:
        # Escape HTML entities to prevent parse errors
        import html
        from io import BytesIO
        import re
        
        sender = html.escape(email_data.get('from', 'Unknown'))
        receiver = html.escape(email_data.get('to', 'Unknown'))
        subject = html.escape(email_data.get('subject', 'No Subject'))
        
        # Get HTML body and convert to Telegram-compatible HTML
        body_html = email_data.get('body_html', '')
        body_plain = email_data.get('body_plain', 'No content')
        
        # Use HTML if available, otherwise plain text
        if body_html:
            # Simple HTML cleanup for Telegram
            # Remove unsupported tags but keep content
            body_content = body_html
            # Remove script and style tags completely
            body_content = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
            body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
            # Convert common HTML tags to Telegram-supported ones
            body_content = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'<b>\1</b>\n', body_content, flags=re.DOTALL)
            body_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'<b>\1</b>', body_content, flags=re.DOTALL)
            body_content = re.sub(r'<em[^>]*>(.*?)</em>', r'<i>\1</i>', body_content, flags=re.DOTALL)
            # Remove other unsupported tags but keep content
            body_content = re.sub(r'<(?!/?(?:b|i|u|s|code|pre|a)[>\s])[^>]+>', '', body_content)
            # Clean up extra whitespace
            body_content = re.sub(r'\n\s*\n', '\n\n', body_content)
            body_content = body_content.strip()
        else:
            # Use plain text and escape it
            body_content = html.escape(body_plain)
        
        # Create header message
        header = f"""
📧 <b>New Email Received!</b>

<b>From:</b> <code>{sender}</code>
<b>To:</b> <code>{receiver}</code>
<b>Subject:</b> {subject}
<b>Attachments:</b> {email_data.get('attachment_count', 0)}

───────────────────────
"""
        
        # Combine header and body
        full_message = header + body_content
        
        # Telegram message limit is 4096 characters
        MAX_LENGTH = 4096
        
        # Split message into chunks if needed
        messages = []
        if len(full_message) <= MAX_LENGTH:
            messages.append(full_message)
        else:
            # Send header first
            messages.append(header)
            
            # Split body into chunks
            remaining = body_content
            chunk_num = 1
            while remaining:
                # Calculate available space (leave room for chunk indicator)
                chunk_header = f"📄 <b>Part {chunk_num}</b>\n\n"
                available = MAX_LENGTH - len(chunk_header)
                
                if len(remaining) <= available:
                    messages.append(chunk_header + remaining)
                    break
                
                # Find a good break point (try to break at newline)
                chunk = remaining[:available]
                last_newline = chunk.rfind('\n')
                if last_newline > available * 0.5:  # If newline is in latter half
                    split_at = last_newline + 1
                else:
                    split_at = available
                
                messages.append(chunk_header + remaining[:split_at])
                remaining = remaining[split_at:]
                chunk_num += 1
        
        # Send all message chunks
        for msg in messages:
            await bot_application.bot.send_message(
                chat_id=telegram_id,
                text=msg,
                parse_mode="HTML"
            )
        
        # Send attachments if any
        attachments = email_data.get('attachments', [])
        if attachments:
            for attachment in attachments[:10]:  # Limit to 10 attachments
                try:
                    filename = attachment.get('filename', 'unnamed')
                    content_type = attachment.get('content_type', 'application/octet-stream')
                    payload = attachment.get('payload', b'')
                    
                    if not payload:
                        continue
                    
                    # Create BytesIO object from payload
                    file_obj = BytesIO(payload)
                    file_obj.name = filename
                    
                    # Send as photo if it's an image
                    if content_type.startswith('image/'):
                        await bot_application.bot.send_photo(
                            chat_id=telegram_id,
                            photo=file_obj,
                            caption=f"📎 {filename}"
                        )
                    else:
                        # Send as document for other file types
                        await bot_application.bot.send_document(
                            chat_id=telegram_id,
                            document=file_obj,
                            caption=f"📎 {filename}"
                        )
                    
                    logger.info(f"Sent attachment: {filename} to user {telegram_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to send attachment {filename}: {e}")
        
        logger.info(f"Email notification sent to user {telegram_id} ({len(messages)} message(s))")
        
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        import traceback
        traceback.print_exc()
