import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID", "YOUR_ADMIN_GROUP_ID")

# Payment Configuration
KPAY_PHONE = os.getenv("KPAY_PHONE", "09XXXXXXXXX")
KPAY_NAME = os.getenv("KPAY_NAME", "Your Name")

# Credit Plans (Number of email accounts)
CREDIT_PLANS = {
    "1_account": {"credits": 1, "price": 2000, "name": "1 Email Account"},
    "3_accounts": {"credits": 3, "price": 5000, "name": "3 Email Accounts"},
    "7_accounts": {"credits": 7, "price": 10000, "name": "7 Email Accounts"},
}

# FastAPI Configuration
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 8000

# Database Configuration (for future use)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./email2telegram.db")
