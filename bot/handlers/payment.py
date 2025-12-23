"""
Payment handler
Handle payment callbacks and receipt uploads
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from database import AsyncSessionLocal, User, Transaction, TransactionStatus
from config import CREDIT_PLANS, KPAY_PHONE, KPAY_NAME, ADMIN_GROUP_ID
import logging

logger = logging.getLogger(__name__)


async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle payment plan selection callback
    """
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    callback_data = query.data
    
    # Extract plan_id from callback_data (format: "buy_1_account")
    if callback_data.startswith("buy_"):
        plan_id = callback_data[4:]  # Remove "buy_" prefix
        
        plan_info = CREDIT_PLANS.get(plan_id)
        if not plan_info:
            await query.edit_message_text(
                "❌ Invalid plan selected. Please try /credits again.",
                parse_mode="HTML"
            )
            return
        
        payment_message = f"""
💰 <b>Payment Instructions</b>

<b>Plan Selected:</b> {plan_info['name']}
<b>Credits:</b> {plan_info['credits']} email account(s)
<b>Amount:</b> {plan_info['price']} MMK

📱 <b>KPay Payment Details:</b>
Phone: <code>{KPAY_PHONE}</code>
Name: {KPAY_NAME}

<b>Steps:</b>
1. Transfer <b>{plan_info['price']} MMK</b> to the above KPay number
2. Take a screenshot of the payment confirmation
3. Send the screenshot here as an <b>image</b> (not as a file)

⏳ After sending, your payment will be reviewed by our admin team.
You'll be notified once approved!

Send /cancel to abort this payment.
        """
        
        await query.edit_message_text(
            payment_message,
            parse_mode="HTML"
        )
        
        # Store payment info in user context
        context.user_data['pending_payment'] = {
            'plan_id': plan_id,
            'plan_info': plan_info,
            'user_id': user.id
        }
        
        logger.info(f"User {user.id} selected payment plan: {plan_id}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle photo uploads (payment receipts)
    """
    user = update.effective_user
    
    # Check if user has pending payment
    payment_info = context.user_data.get('pending_payment')
    
    if not payment_info:
        # No pending payment, ignore the photo
        logger.info(f"User {user.id} sent photo without pending payment - ignoring")
        return
    
    # Get the largest photo (best quality)
    photo = update.message.photo[-1]
    photo_file_id = photo.file_id
    
    async with AsyncSessionLocal() as session:
        # Get user from database
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            await update.message.reply_text(
                "⚠️ Please use /start first to register.",
                parse_mode="HTML"
            )
            return
        
        # Create transaction record
        new_transaction = Transaction(
            user_id=user.id,
            amount=payment_info['plan_info']['price'],
            plan_type=payment_info['plan_id'],
            receipt_photo_id=photo_file_id,
            status=TransactionStatus.PENDING
        )
        session.add(new_transaction)
        await session.commit()
        
        # Refresh to get the ID
        await session.refresh(new_transaction)
        transaction_id = new_transaction.id
        
        logger.info(f"Transaction created: ID={transaction_id}, User={user.id}, Plan={payment_info['plan_id']}")
    
    # Send confirmation to user
    await update.message.reply_text(
        "✅ <b>Payment Receipt Received!</b>\n\n"
        f"Plan: {payment_info['plan_info']['name']}\n"
        f"Amount: {payment_info['plan_info']['price']} MMK\n\n"
        "⏳ Your payment is being reviewed by our admin team.\n"
        "You'll receive a notification once it's approved.\n\n"
        "Thank you for your patience! 🙏",
        parse_mode="HTML"
    )
    
    # Forward to admin group with approval buttons
    try:
        admin_message = f"""
🔔 <b>New Payment Received</b>

<b>Transaction ID:</b> #{transaction_id}
<b>User:</b> {user.first_name} {user.last_name or ''}
<b>Username:</b> @{user.username or 'N/A'}
<b>User ID:</b> <code>{user.id}</code>

<b>Plan:</b> {payment_info['plan_info']['name']}
<b>Credits:</b> {payment_info['plan_info']['credits']} email(s)
<b>Amount:</b> {payment_info['plan_info']['price']} MMK

<b>Status:</b> ⏳ Pending Review
        """
        
        # Create admin approval buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{transaction_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{transaction_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send photo with caption to admin group
        await context.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=photo_file_id,
            caption=admin_message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        
        logger.info(f"Payment notification sent to admin group for transaction {transaction_id}")
        
    except Exception as e:
        logger.error(f"Failed to send to admin group: {e}")
        await update.message.reply_text(
            "⚠️ Payment received but failed to notify admin. Please contact support.",
            parse_mode="HTML"
        )
    
    # Clear pending payment from context
    context.user_data.pop('pending_payment', None)
