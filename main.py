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
        
        print("\n" + "="*80)
        print("📧 NEW EMAIL RECEIVED")
        print("="*80)
        
        # Parse the email using mailparser
        mail = mailparser.parse_from_bytes(body)
        
        # Extract all possible fields
        print("\n📋 BASIC INFORMATION:")
        print(f"From: {mail.from_}")
        print(f"To: {mail.to}")
        print(f"CC: {mail.cc}")
        print(f"BCC: {mail.bcc}")
        print(f"Subject: {mail.subject}")
        print(f"Date: {mail.date}")
        print(f"Message-ID: {mail.message_id}")
        
        print("\n📝 EMAIL BODY:")
        print(f"Plain Text Body:\n{mail.text_plain}")
        print(f"\nHTML Body:\n{mail.text_html}")
        
        print("\n📎 ATTACHMENTS:")
        attachment_count = 0
        if mail.attachments:
            attachment_count = len(mail.attachments)
            for idx, attachment in enumerate(mail.attachments):
                print(f"  [{idx+1}] Filename: {attachment.get('filename', 'N/A')}")
                print(f"      Content-Type: {attachment.get('mail_content_type', 'N/A')}")
                print(f"      Size: {len(attachment.get('payload', b''))} bytes")
        else:
            print("  No attachments")
        
        print("\n🔍 HEADERS:")
        if mail.headers:
            for key, value in mail.headers.items():
                print(f"  {key}: {value}")
        
        print("\n📊 ADDITIONAL METADATA:")
        print(f"Received: {mail.received}")
        print(f"Reply-To: {mail.reply_to}")
        print(f"Delivered-To: {mail.delivered_to}")
        
        # TODO: Database integration
        # 1. Look up receiver email in UserEmails table to find user_id
        # 2. Log email in EmailLogs table
        # 3. Get user's telegram_id from Users table
        
        # For now, just prepare the email data
        email_data = {
            'from': mail.from_,
            'to': mail.to,
            'subject': mail.subject,
            'body_plain': mail.text_plain or '',
            'body_html': mail.text_html or '',
            'attachment_count': attachment_count,
            'date': str(mail.date)
        }
        
        # TODO: Send notification to user via Telegram
        # Example (once database is integrated):
        # user_telegram_id = get_user_telegram_id_from_email(mail.to)
        # if user_telegram_id and bot_app:
        #     await send_email_notification(user_telegram_id, email_data, bot_app)
        
        print("\n💬 TELEGRAM NOTIFICATION:")
        print("(Will be sent once database integration is complete)")
        
        print("\n" + "="*80)
        print("✅ EMAIL PROCESSING COMPLETE")
        print("="*80 + "\n")
        
        # Return success response to Cloudflare
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Email received and parsed successfully",
                "email_info": {
                    "from": mail.from_,
                    "to": mail.to,
                    "subject": mail.subject,
                    "date": str(mail.date),
                    "has_attachments": attachment_count > 0
                }
            }
        )
        
    except Exception as e:
        print(f"\n❌ ERROR PROCESSING EMAIL: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
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

