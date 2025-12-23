# Handler Files Structure

## 📁 New Modular Structure

```
bot/
├── __init__.py                    # Bot package exports
├── bot.py                         # Bot application setup
│
└── handlers/                      # Handler modules (NEW)
    ├── __init__.py               # Exports all handlers
    ├── start.py                  # /start command
    ├── credits.py                # /credits command
    ├── add_email.py              # /add_email command
    ├── my_emails.py              # /my_emails command
    ├── help.py                   # /help command
    ├── payment.py                # Payment flow handlers
    └── admin.py                  # Admin approval handlers
```

## 📝 Handler Files Overview

### `handlers/start.py`
**Command:** `/start`
**Purpose:** User onboarding and welcome message
**Functions:**
- `start_command()` - Displays welcome message and quick start guide

---

### `handlers/credits.py`
**Command:** `/credits`
**Purpose:** Check balance and purchase credits
**Functions:**
- `credits_command()` - Shows current balance and payment plan options

**Features:**
- Displays current credit balance
- Lists all available plans with prices
- Inline keyboard buttons for plan selection

---

### `handlers/add_email.py`
**Command:** `/add_email`
**Purpose:** Create new email aliases
**Functions:**
- `add_email_command()` - Email creation interface

**Features:**
- Credit balance check
- Available domains listing
- Email validation rules
- Accepts email as command argument

---

### `handlers/my_emails.py`
**Command:** `/my_emails`
**Purpose:** List user's email addresses
**Functions:**
- `my_emails_command()` - Displays all user emails

**Features:**
- Shows empty state if no emails
- Lists all emails with creation date and domain

---

### `handlers/help.py`
**Command:** `/help`
**Purpose:** Show help information
**Functions:**
- `help_command()` - Comprehensive help text

**Features:**
- All available commands
- Credit system explanation
- Payment process guide
- Privacy information

---

### `handlers/payment.py`
**Purpose:** Handle payment flow
**Functions:**
- `handle_payment_callback()` - Process plan selection
- `handle_photo()` - Handle receipt uploads

**Features:**
- Shows KPay payment details
- User state management
- Receipt confirmation
- Admin notification (TODO)

**Callback Patterns:**
- `buy_*` - Payment plan selection

---

### `handlers/admin.py`
**Purpose:** Admin approval system
**Functions:**
- `handle_admin_callback()` - Process approve/reject actions

**Features:**
- Transaction approval
- Transaction rejection
- User notification (TODO)
- Credit addition (TODO)

**Callback Patterns:**
- `approve_*` - Approve transaction
- `reject_*` - Reject transaction

---

## 🔍 Benefits of This Structure

### 1. **Easy Debugging**
- Each handler in its own file
- Clear separation of concerns
- Easy to locate specific functionality

### 2. **Better Organization**
- Logical grouping of related functions
- Easier to navigate codebase
- Clear file naming convention

### 3. **Maintainability**
- Smaller, focused files
- Easier to test individual handlers
- Reduced merge conflicts

### 4. **Scalability**
- Easy to add new commands
- Simple to extend existing handlers
- Clear pattern to follow

---

## 🚀 Adding a New Command

To add a new command, follow this pattern:

1. **Create new handler file:**
   ```
   bot/handlers/your_command.py
   ```

2. **Write the handler:**
   ```python
   from telegram import Update
   from telegram.ext import ContextTypes
   import logging

   logger = logging.getLogger(__name__)

   async def your_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Your command description"""
       user = update.effective_user
       
       # Your logic here
       
       await update.message.reply_text("Response")
       logger.info(f"User {user.id} used your_command")
   ```

3. **Export in `handlers/__init__.py`:**
   ```python
   from .your_command import your_command
   
   __all__ = [
       # ... existing exports
       'your_command'
   ]
   ```

4. **Register in `bot/bot.py`:**
   ```python
   from bot.handlers import your_command
   
   # In create_bot_application():
   application.add_handler(CommandHandler("yourcommand", your_command))
   ```

---

## 📊 Handler Registration Flow

```
handlers/__init__.py
    ↓ (exports)
bot/bot.py
    ↓ (imports & registers)
main.py
    ↓ (creates bot application)
Telegram Bot Running
```

---

## 🔧 Current TODO Items

All handlers have placeholder logic marked with `# TODO:` comments:

- [ ] Database integration for user data
- [ ] Credit balance tracking
- [ ] Email validation and creation
- [ ] Transaction logging
- [ ] Admin group forwarding
- [ ] User notifications
- [ ] Email-to-user mapping

These will be implemented in the next phase (database integration).

---

## 📝 Logging

Each handler includes logging for debugging:
- User actions logged with user ID
- Command usage tracking
- Error logging (when implemented)
- State changes

Check console output to see handler activity in real-time.
