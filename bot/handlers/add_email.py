"""
/add_email command handler
Create new email aliases with validation and database integration
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import select
from database import AsyncSessionLocal, User, Domain, UserEmail
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_EMAIL = 1


async def add_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_email command - Create a new email alias
    Shows available domains and asks for email input
    """
    user = update.effective_user
    
    async with AsyncSessionLocal() as session:
        # Fetch user with credit balance
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            await update.message.reply_text(
                "⚠️ Please use /start first to register.",
                parse_mode="HTML"
            )
            return ConversationHandler.END
        
        # Check credits
        if db_user.credits <= 0:
            await update.message.reply_text(
                "❌ <b>Insufficient Credits</b>\n\n"
                "You don't have any credits to create an email address.\n"
                "Use /credits to purchase more credits.",
                parse_mode="HTML"
            )
            logger.info(f"User {user.id} tried to add email with 0 credits")
            return ConversationHandler.END
        
        # Fetch active domains with expiry info
        result = await session.execute(
            select(Domain)
            .where(Domain.is_active == True)
            .order_by(Domain.domain_name)
        )
        domains = result.scalars().all()
        
        if not domains:
            await update.message.reply_text(
                "❌ <b>No Domains Available</b>\n\n"
                "There are no active domains at the moment.\n"
                "Please contact support.",
                parse_mode="HTML"
            )
            logger.warning("No active domains found")
            return ConversationHandler.END
        
        # Build domain list with expiry info
        message = f"""
📧 <b>Create New Email Address</b>

Available Credits: <b>{db_user.credits}</b>

🌐 <b>Available Domains:</b>

"""
        
        for idx, domain in enumerate(domains, 1):
            message += f"{idx}. <code>@{domain.domain_name}</code>"
            
            # Add expiry info if available
            if domain.expiry_date:
                days_left = (domain.expiry_date - datetime.utcnow()).days
                expiry_str = domain.expiry_date.strftime('%Y-%m-%d')
                
                if days_left < 0:
                    message += f" ⚠️ <i>Expired</i>"
                elif days_left <= 30:
                    message += f" ⏰ <i>Expires: {expiry_str} ({days_left} days left)</i>"
                else:
                    message += f" ✅ <i>Expires: {expiry_str} ({days_left} days left)</i>"
            else:
                message += " ✅ <i>No expiry</i>"
            
            message += "\n"
        
        # Create personalized example with user's first name
        user_first_name = user.first_name.lower().replace(" ", "")
        user_last_name = user.last_name.lower().replace(" ", "") if user.last_name else ""
        
        if user_last_name:
            example_email = f"{user_first_name}.{user_last_name}@{domains[0].domain_name}"
        else:
            example_email = f"{user_first_name}@{domains[0].domain_name}"
        
        message += f"""

📝 <b>How to create:</b>
<b>Rules:</b>
• Only lowercase letters, numbers, dots, and hyphens
• Must start with a letter
• 3-30 characters before @
• Must use one of the available domains above

<b>Example for you:</b>
<code>{example_email}</code>

Send /cancel to abort.
        """
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"User {user.id} started email creation process")
        
        # Store available domains in context for validation
        context.user_data['available_domains'] = [d.domain_name for d in domains]
        context.user_data['domain_objects'] = {d.domain_name: d for d in domains}
        
        return WAITING_FOR_EMAIL


async def handle_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle user's email input and validate it
    """
    user = update.effective_user
    
    # Check if user has pending payment - if so, ignore text and ask for photo
    if context.user_data.get('pending_payment'):
        await update.message.reply_text(
            "⚠️ <b>Please send a photo</b>\n\n"
            "You have a pending payment. Please send your payment receipt as an <b>image</b> (not text).\n\n"
            "If you want to cancel the payment, send /cancel",
            parse_mode="HTML"
        )
        return WAITING_FOR_EMAIL
    
    email_input = update.message.text.strip().lower()
    
    # Validate email format
    email_pattern = r'^[a-z][a-z0-9.-]{2,29}@[a-z0-9.-]+\.[a-z]{2,}$'
    if not re.match(email_pattern, email_input):
        await update.message.reply_text(
            "❌ <b>Invalid Email Format</b>\n\n"
            "Please follow the rules:\n"
            "• Start with a letter\n"
            "• Use only lowercase letters, numbers, dots, and hyphens\n"
            "• 3-30 characters before @\n\n"
            "Try again or send /cancel to abort.",
            parse_mode="HTML"
        )
        return WAITING_FOR_EMAIL
    
    # Split email into local and domain parts
    try:
        local_part, domain_part = email_input.split('@')
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid email format. Please include @ symbol.\n\n"
            "Try again or send /cancel to abort.",
            parse_mode="HTML"
        )
        return WAITING_FOR_EMAIL
    
    # Check if domain is in available domains
    available_domains = context.user_data.get('available_domains', [])
    if domain_part not in available_domains:
        # Build available domains list
        domains_list = "\n".join([f"• <code>@{d}</code>" for d in available_domains])
        
        # Create personalized example with user's first name
        user_first_name = user.first_name.lower().replace(" ", "")
        user_last_name = user.last_name.lower().replace(" ", "") if user.last_name else ""
        
        if user_last_name:
            example_email = f"{user_first_name}.{user_last_name}@{available_domains[0]}"
        else:
            example_email = f"{user_first_name}@{available_domains[0]}"
        
        await update.message.reply_text(
            f"❌ <b>Invalid Domain</b>\n\n"
            f"The domain <code>@{domain_part}</code> is not available.\n\n"
            f"<b>Available domains:</b>\n{domains_list}\n\n"
            f"<b>Example for you:</b>\n<code>{example_email}</code>\n\n"
            f"Try again or send /cancel to abort.",
            parse_mode="HTML"
        )
        return WAITING_FOR_EMAIL
    
    # Check database for existing email and create new one
    async with AsyncSessionLocal() as session:
        # Check if email already exists
        result = await session.execute(
            select(UserEmail).where(UserEmail.email_address == email_input)
        )
        existing_email = result.scalar_one_or_none()
        
        if existing_email:
            await update.message.reply_text(
                f"❌ <b>Email Already Exists</b>\n\n"
                f"The email <code>{email_input}</code> is already taken.\n\n"
                f"Please choose a different email address.\n\n"
                f"Try again or send /cancel to abort.",
                parse_mode="HTML"
            )
            return WAITING_FOR_EMAIL
        
        # Get user and domain objects
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        domain_objects = context.user_data.get('domain_objects', {})
        domain_obj = domain_objects.get(domain_part)
        
        if not db_user or not domain_obj:
            await update.message.reply_text(
                "❌ An error occurred. Please try /add_email again.",
                parse_mode="HTML"
            )
            return ConversationHandler.END
        
        # Double-check credits
        if db_user.credits <= 0:
            await update.message.reply_text(
                "❌ <b>Insufficient Credits</b>\n\n"
                "You don't have any credits left.",
                parse_mode="HTML"
            )
            return ConversationHandler.END
        
        # Create new email
        new_email = UserEmail(
            user_id=db_user.telegram_id,
            email_address=email_input,
            domain_id=domain_obj.id
        )
        session.add(new_email)
        
        # Deduct credit
        db_user.credits -= 1
        
        await session.commit()
        
        # Success message
        success_message = f"""
✅ <b>Email Created Successfully!</b>

📧 <b>Your new email:</b> <code>{email_input}</code>
🌐 <b>Domain:</b> {domain_part}
💳 <b>Remaining Credits:</b> {db_user.credits}

🎉 <b>You're all set!</b>

Any emails sent to <code>{email_input}</code> will be forwarded to this Telegram chat.

Use /my_emails to see all your email addresses.
        """
        
        await update.message.reply_text(success_message, parse_mode="HTML")
        logger.info(f"User {user.id} created email: {email_input} (Credits left: {db_user.credits})")
        
        # Clear context
        context.user_data.clear()
        
        return ConversationHandler.END


async def cancel_email_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancel email creation conversation
    """
    await update.message.reply_text(
        "❌ Email creation cancelled.\n\n"
        "Use /add_email to try again.",
        parse_mode="HTML"
    )
    logger.info(f"User {update.effective_user.id} cancelled email creation")
    context.user_data.clear()
    return ConversationHandler.END
