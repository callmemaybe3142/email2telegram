from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import mailparser
from datetime import datetime
import asyncio
import logging
from contextlib import asynccontextmanager

from bot import create_bot_application, send_email_notification
from config import FASTAPI_HOST, FASTAPI_PORT
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global bot application instance
bot_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to start/stop Telegram bot with FastAPI
    """
    global bot_app
    
    # Startup: Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    # Startup: Initialize and start Telegram bot
    logger.info("Starting Telegram bot...")
    bot_app = create_bot_application()
    await bot_app.initialize()
    await bot_app.start()
    
    # Start polling in background
    asyncio.create_task(bot_app.updater.start_polling(drop_pending_updates=True))
    logger.info("✅ Telegram bot started successfully")
    
    yield
    
    # Shutdown: Stop Telegram bot
    logger.info("Stopping Telegram bot...")
    try:
        # Set a timeout for shutdown
        async def shutdown_with_timeout():
            if bot_app.updater.running:
                await bot_app.updater.stop()
            await bot_app.stop()
            await bot_app.shutdown()
        
        # Wait max 5 seconds for shutdown
        await asyncio.wait_for(shutdown_with_timeout(), timeout=5.0)
        logger.info("✅ Telegram bot stopped")
    except asyncio.TimeoutError:
        logger.warning("⚠️ Bot shutdown timed out, forcing exit")
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")



app = FastAPI(
    title="Email to Telegram Webhook",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "status": "Email2Telegram Service Running",
        "services": ["FastAPI Webhook", "Telegram Bot"],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook/email")
async def receive_email(request: Request):
    """
    Webhook endpoint to receive raw MIME email from Cloudflare Email Worker
    """
    try:
        # Get the raw body
        body = await request.body()
        
        logger.info("="*80)
        logger.info("📧 NEW EMAIL RECEIVED")
        logger.info("="*80)
        
        # Parse the email using mailparser
        mail = mailparser.parse_from_bytes(body)
        
        # Extract recipient email (first 'to' address)
        recipient_email = None
        if isinstance(mail.to, list) and len(mail.to) > 0:
            recipient_email = mail.to[0][1] if isinstance(mail.to[0], tuple) else mail.to[0]
        elif isinstance(mail.to, str):
            recipient_email = mail.to
        
        if not recipient_email:
            logger.error("No recipient email found in the message")
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "No recipient email found"}
            )
        
        recipient_email = recipient_email.lower().strip()
        logger.info(f"Recipient: {recipient_email}")
        
        # Extract sender
        sender_email = None
        if isinstance(mail.from_, list) and len(mail.from_) > 0:
            sender_email = mail.from_[0][1] if isinstance(mail.from_[0], tuple) else mail.from_[0]
        elif isinstance(mail.from_, str):
            sender_email = mail.from_
        
        sender_email = sender_email or "Unknown"
        logger.info(f"Sender: {sender_email}")
        logger.info(f"Subject: {mail.subject}")
        
        # Count attachments and extract them
        attachments = []
        if mail.attachments:
            for attachment in mail.attachments:
                attachments.append({
                    'filename': attachment.get('filename', 'unnamed'),
                    'content_type': attachment.get('mail_content_type', 'application/octet-stream'),
                    'payload': attachment.get('payload', b''),
                    'size': len(attachment.get('payload', b''))
                })
        
        attachment_count = len(attachments)
        
        # Database lookup and notification
        from database import AsyncSessionLocal, UserEmail, User, EmailLog
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        async with AsyncSessionLocal() as session:
            # Find the user email record
            result = await session.execute(
                select(UserEmail)
                .options(selectinload(UserEmail.user))
                .where(UserEmail.email_address == recipient_email)
            )
            user_email = result.scalar_one_or_none()
            
            if not user_email:
                logger.warning(f"Email address '{recipient_email}' not found in database")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "error",
                        "message": f"Email address '{recipient_email}' not registered"
                    }
                )
            
            # Get the user
            db_user = user_email.user
            if not db_user:
                logger.error(f"User not found for email '{recipient_email}'")
                return JSONResponse(
                    status_code=200,
                    content={"status": "error", "message": "User not found"}
                )
            
            telegram_id = db_user.telegram_id
            logger.info(f"Found user: {db_user.first_name} (Telegram ID: {telegram_id})")
            
            # Prepare email body (handle both string and list)
            body_html = mail.text_html
            if isinstance(body_html, list):
                body_html = '\n'.join(body_html) if body_html else ""
            elif body_html is None:
                body_html = mail.text_plain or ""
            
            if isinstance(body_html, list):
                body_html = '\n'.join(str(item) for item in body_html)
            
            body_html = str(body_html) if body_html else ""
            
            # Store email in database
            email_log = EmailLog(
                user_id=telegram_id,
                sender=sender_email,
                receiver=recipient_email,
                subject=mail.subject or "No Subject",
                body_html=body_html,
                timestamp=datetime.utcnow()
            )
            session.add(email_log)
            await session.commit()
            
            logger.info(f"Email logged to database (ID: {email_log.id})")
        
        # Prepare email data for notification
        body_plain = mail.text_plain
        if isinstance(body_plain, list):
            body_plain = '\n'.join(str(item) for item in body_plain) if body_plain else ""
        elif body_plain is None:
            body_plain = body_html or "No content"
        
        body_plain = str(body_plain) if body_plain else "No content"
        
        email_data = {
            'from': sender_email,
            'to': recipient_email,
            'subject': mail.subject or "No Subject",
            'body_plain': body_plain,
            'body_html': body_html,  # Add HTML body for better formatting
            'attachment_count': attachment_count,
            'attachments': attachments,
            'date': str(mail.date) if mail.date else "Unknown"
        }
        
        # Send Telegram notification
        if bot_app:
            try:
                await send_email_notification(telegram_id, email_data, bot_app)
                logger.info(f"✅ Telegram notification sent to user {telegram_id}")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {e}")
        else:
            logger.warning("Bot application not available - notification not sent")
        
        logger.info("="*80)
        logger.info("✅ EMAIL PROCESSING COMPLETE")
        logger.info("="*80)
        
        # Return success response to Cloudflare
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Email received and delivered",
                "email_info": {
                    "from": sender_email,
                    "to": recipient_email,
                    "subject": mail.subject,
                    "delivered_to_telegram": telegram_id
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ ERROR PROCESSING EMAIL: {str(e)}")
        logger.error(f"Error Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Still return 200 to Cloudflare to avoid retries
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Error processing email: {str(e)}"
            }
        )



if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Email2Telegram Service...")
    logger.info(f"FastAPI server: http://{FASTAPI_HOST}:{FASTAPI_PORT}")
    
    try:
        uvicorn.run(
            app,
            host=FASTAPI_HOST,
            port=FASTAPI_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        import sys
        sys.exit(0)

