# ✅ Pricing Structure Updated!

## New Pricing

The credit plans have been updated to reflect the actual pricing structure:

| Plan | Email Accounts | Price |
|------|----------------|-------|
| **Basic** | 1 account | 2,000 MMK |
| **Standard** | 3 accounts | 5,000 MMK |
| **Premium** | 7 accounts | 10,000 MMK |

## Changes Made

### 1. Updated `config.py`
Changed from monthly subscription model to account-based pricing:

**Before:**
```python
CREDIT_PLANS = {
    "1_month": {"credits": 1, "price": 1000, "duration": "1 month"},
    "3_months": {"credits": 3, "price": 2500, "duration": "3 months"},
    # ...
}
```

**After:**
```python
CREDIT_PLANS = {
    "1_account": {"credits": 1, "price": 2000, "name": "1 Email Account"},
    "3_accounts": {"credits": 3, "price": 5000, "name": "3 Email Accounts"},
    "7_accounts": {"credits": 7, "price": 10000, "name": "7 Email Accounts"},
}
```

### 2. Updated Handlers

**Files Modified:**
- ✅ `bot/handlers/credits.py` - Plan display and buttons
- ✅ `bot/handlers/payment.py` - Payment instructions
- ✅ `bot/handlers/help.py` - Help text with pricing

**Changes:**
- Replaced `duration` with `name` throughout
- Updated terminology from "email(s)" to "email account(s)"
- Added pricing section to help command

## What Users Will See

### `/credits` Command
```
💳 Your Credit Balance

Current Credits: 1 email(s)

📦 Available Plans:

• 1 Email Account: 2000 MMK
• 3 Email Accounts: 5000 MMK
• 7 Email Accounts: 10000 MMK

💰 Purchase Credits:
Select a plan below to proceed with payment.

[🎫 1 Email Account - 2000 MMK]
[🎫 3 Email Accounts - 5000 MMK]
[🎫 7 Email Accounts - 10000 MMK]
```

### Payment Instructions
```
💰 Payment Instructions

Plan Selected: 3 Email Accounts
Credits: 3 email account(s)
Amount: 5000 MMK

📱 KPay Payment Details:
Phone: 09XXXXXXXXX
Name: Your Name

Steps:
1. Transfer 5000 MMK to the above KPay number
2. Take a screenshot of the payment confirmation
3. Send the screenshot here
```

### `/help` Command
Now includes pricing information:
```
Pricing:
• 1 Email Account - 2000 MMK
• 3 Email Accounts - 5000 MMK
• 7 Email Accounts - 10000 MMK
```

## Testing

Test the updated pricing by:

1. **Send `/credits`** - Should show new prices
2. **Click a plan** - Should show correct amount
3. **Send `/help`** - Should display pricing section

All prices are now in MMK (Myanmar Kyat) and reflect the account-based model.

## Notes

- Each credit = 1 email account (permanent, not time-based)
- Prices are final and include all features
- No expiration dates on accounts
- Credits are deducted when creating an email address
