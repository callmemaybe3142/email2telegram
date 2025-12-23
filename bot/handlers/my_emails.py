"""
/my_emails command handler
List all user's email addresses
"""

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import AsyncSessionLocal, User, UserEmail, Domain
import logging

logger = logging.getLogger(__name__)


async def my_emails_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /my_emails command - List all user's email addresses
    """
    user = update.effective_user
    
    async with AsyncSessionLocal() as session:
        # Fetch user with their emails and domains
        result = await session.execute(
            select(User)
            .options(
                selectinload(User.emails).selectinload(UserEmail.domain)
            )
            .where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            # User not found (shouldn't happen if they used /start)
            await update.message.reply_text(
                "⚠️ Please use /start first to register.",
                parse_mode="HTML"
            )
            logger.warning(f"User {user.id} not found in database")
            return
        
        user_emails = db_user.emails
        
        if not user_emails:
            message = """
📭 <b>Your Email Addresses</b>

You don't have any email addresses yet.

Use /add_email to create your first email address!
            """
        else:
            message = f"📬 <b>Your Email Addresses</b>\n\n"
            message += f"Total: <b>{len(user_emails)}</b> email(s)\n"
            message += f"Available Credits: <b>{db_user.credits}</b>\n\n"
            message += "─" * 20 + "\n"
            
            for idx, email in enumerate(user_emails, 1):
                domain_name = email.domain.domain_name if email.domain else "Unknown"
                domain_status = "✅" if (email.domain and email.domain.is_active) else "❌"
                created = email.created_at.strftime('%Y-%m-%d %H:%M')
                
                message += f"<b>{idx}.</b> <code>{email.email_address}</code>\n"
                message += f"   📅 Created: {created}\n"
                message += f"   🌐 Domain: {domain_name} {domain_status}\n"
                
                # Show domain expiry if available
                if email.domain and email.domain.expiry_date:
                    expiry = email.domain.expiry_date.strftime('%Y-%m-%d')
                    message += f"   ⏰ Expires: {expiry}\n"
                
                message += "\n"
            
            message += "─" * 20 + "\n"
            message += "\n💡 <b>Tip:</b> Use /add_email to create more addresses!"
    
    await update.message.reply_text(message, parse_mode="HTML")
    logger.info(f"User {user.id} viewed their emails ({len(user_emails)} total)")

