"""
Admin handler
Handle payment approval/rejection
"""

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from database import AsyncSessionLocal, User, Transaction, TransactionStatus
import logging

logger = logging.getLogger(__name__)


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle admin approval/rejection callbacks
    """
    query = update.callback_query
    await query.answer()
    
    admin_user = update.effective_user
    callback_data = query.data
    
    # Parse callback data (format: "approve_123" or "reject_123")
    action, transaction_id_str = callback_data.split('_', 1)
    
    try:
        transaction_id = int(transaction_id_str)
    except ValueError:
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ Invalid transaction ID.",
            parse_mode="HTML"
        )
        return
    
    async with AsyncSessionLocal() as session:
        # Fetch transaction
        result = await session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ Transaction not found.",
                parse_mode="HTML"
            )
            logger.warning(f"Transaction {transaction_id} not found")
            return
        
        # Check if already processed
        if transaction.status != TransactionStatus.PENDING:
            status_emoji = "✅" if transaction.status == TransactionStatus.APPROVED else "❌"
            await query.edit_message_caption(
                caption=query.message.caption + f"\n\n{status_emoji} Already processed: {transaction.status.value}",
                parse_mode="HTML"
            )
            return
        
        # Fetch user
        result = await session.execute(
            select(User).where(User.telegram_id == transaction.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ User not found in database.",
                parse_mode="HTML"
            )
            logger.error(f"User {transaction.user_id} not found for transaction {transaction_id}")
            return
        
        if action == "approve":
            # Approve payment - add credits to user
            from config import CREDIT_PLANS
            plan_info = CREDIT_PLANS.get(transaction.plan_type)
            
            if not plan_info:
                await query.edit_message_caption(
                    caption=query.message.caption + "\n\n❌ Invalid plan type.",
                    parse_mode="HTML"
                )
                return
            
            # Add credits
            credits_to_add = plan_info['credits']
            user.credits += credits_to_add
            
            # Update transaction status
            transaction.status = TransactionStatus.APPROVED
            
            await session.commit()
            
            # Update admin message
            updated_caption = query.message.caption.replace(
                "⏳ Pending Review",
                f"✅ Approved by @{admin_user.username or admin_user.first_name}"
            )
            updated_caption += f"\n\n<b>Credits Added:</b> {credits_to_add}\n<b>New Balance:</b> {user.credits}"
            
            await query.edit_message_caption(
                caption=updated_caption,
                parse_mode="HTML"
            )
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=transaction.user_id,
                    text=f"""
✅ <b>Payment Approved!</b>

Your payment has been approved by our admin team.

<b>Plan:</b> {plan_info['name']}
<b>Credits Added:</b> {credits_to_add}
<b>New Balance:</b> {user.credits} credit(s)

🎉 You can now create email addresses using /add_email

Thank you for your purchase! 🙏
                    """,
                    parse_mode="HTML"
                )
                logger.info(f"Transaction {transaction_id} approved by admin {admin_user.id}. User {user.telegram_id} credited with {credits_to_add}")
            except Exception as e:
                logger.error(f"Failed to notify user {transaction.user_id}: {e}")
        
        elif action == "reject":
            # Reject payment
            transaction.status = TransactionStatus.REJECTED
            
            await session.commit()
            
            # Update admin message
            updated_caption = query.message.caption.replace(
                "⏳ Pending Review",
                f"❌ Rejected by @{admin_user.username or admin_user.first_name}"
            )
            
            await query.edit_message_caption(
                caption=updated_caption,
                parse_mode="HTML"
            )
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=transaction.user_id,
                    text="""
❌ <b>Payment Rejected</b>

Unfortunately, your payment could not be verified.

<b>Possible reasons:</b>
• Incorrect payment amount
• Payment screenshot unclear
• Payment not received

Please try again with /credits or contact support if you believe this is an error.
                    """,
                    parse_mode="HTML"
                )
                logger.info(f"Transaction {transaction_id} rejected by admin {admin_user.id}")
            except Exception as e:
                logger.error(f"Failed to notify user {transaction.user_id}: {e}")
