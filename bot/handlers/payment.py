"""
Payment flow handlers
Handle payment callbacks and receipt uploads
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import CREDIT_PLANS, KPAY_PHONE, KPAY_NAME
import logging

logger = logging.getLogger(__name__)


async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline keyboard callbacks for payment plan selection
    """
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data.startswith("buy_"):
        plan_id = callback_data.replace("buy_", "")
        plan_info = CREDIT_PLANS.get(plan_id)
        
        if not plan_info:
            await query.edit_message_text("❌ Invalid plan selected.")
            logger.warning(f"Invalid plan selected: {plan_id}")
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
3. Send the screenshot here

⏳ After sending, your payment will be reviewed by our admin team.
You'll be notified once approved!
        """
        
        await query.edit_message_text(
            payment_message,
            parse_mode="HTML"
        )
        
        # Set user state to waiting for payment screenshot
        context.user_data['awaiting_payment'] = {
            'plan_id': plan_id,
            'plan_info': plan_info
        }
        
        logger.info(f"User {query.from_user.id} selected plan: {plan_id}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle photo uploads (payment receipts)
    """
    user = update.effective_user
    
    # Check if user is in payment flow
    if 'awaiting_payment' not in context.user_data:
        await update.message.reply_text(
            "ℹ️ If you're trying to submit a payment receipt, "
            "please use /credits first to select a plan."
        )
        logger.info(f"User {user.id} sent photo without payment context")
        return
    
    payment_info = context.user_data['awaiting_payment']
    photo = update.message.photo[-1]  # Get highest resolution
    
    # TODO: Save transaction to database with 'pending' status
    # TODO: Forward to admin group with approval buttons
    
    await update.message.reply_text(
        "✅ <b>Payment Receipt Received!</b>\n\n"
        f"Plan: {payment_info['plan_info']['name']}\n"
        f"Amount: {payment_info['plan_info']['price']} MMK\n\n"
        "⏳ Your payment is being reviewed by our admin team.\n"
        "You'll receive a notification once it's approved.\n\n"
        "Thank you for your patience! 🙏",
        parse_mode="HTML"
    )
    
    # TODO: Forward to admin group
    # admin_message = f"""
    # 🔔 **New Payment Submission**
    # 
    # User: {user.first_name} (@{user.username})
    # User ID: {user.id}
    # Plan: {payment_info['plan_info']['duration']}
    # Credits: {payment_info['plan_info']['credits']}
    # Amount: {payment_info['plan_info']['price']} MMK
    # """
    # 
    # keyboard = [
    #     [
    #         InlineKeyboardButton("✅ Approve", callback_data=f"approve_{transaction_id}"),
    #         InlineKeyboardButton("❌ Reject", callback_data=f"reject_{transaction_id}")
    #     ]
    # ]
    
    # Clear payment state
    del context.user_data['awaiting_payment']
    
    logger.info(f"Payment receipt received from user {user.id} for plan {payment_info['plan_id']}")
