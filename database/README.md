# Database Schema Documentation

## Overview

The Email2Telegram service uses **SQLite** with **async SQLAlchemy** for data persistence. The database uses WAL (Write-Ahead Logging) mode for better concurrency.

## Database Tables

### 1. Users Table
Stores Telegram user information and credit balance.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `telegram_id` | BigInteger | PRIMARY KEY | Telegram user ID |
| `username` | String(255) | NULLABLE | Telegram username |
| `first_name` | String(255) | NOT NULL | User's first name |
| `last_name` | String(255) | NULLABLE | User's last name |
| `credits` | Integer | DEFAULT 1 | Available email credits |
| `created_at` | DateTime | DEFAULT NOW | Account creation time |

**Relationships:**
- One-to-Many with `UserEmail`
- One-to-Many with `EmailLog`
- One-to-Many with `Transaction`

---

### 2. Domains Table
Stores available email domains for creating aliases.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Domain ID |
| `domain_name` | String(255) | UNIQUE, NOT NULL | Domain name (e.g., example.com) |
| `expiry_date` | DateTime | NULLABLE | Domain expiration date |
| `is_active` | Boolean | DEFAULT TRUE | Whether domain is active |
| `created_at` | DateTime | DEFAULT NOW | Domain creation time |

**Relationships:**
- One-to-Many with `UserEmail`

---

### 3. UserEmails Table
Stores user email addresses (aliases).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Email ID |
| `user_id` | BigInteger | FOREIGN KEY → Users | Owner of the email |
| `email_address` | String(255) | UNIQUE, NOT NULL | Full email address |
| `domain_id` | Integer | FOREIGN KEY → Domains | Associated domain |
| `created_at` | DateTime | DEFAULT NOW | Email creation time |

**Relationships:**
- Many-to-One with `User`
- Many-to-One with `Domain`

---

### 4. EmailLogs Table
Stores received email logs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Log ID |
| `user_id` | BigInteger | FOREIGN KEY → Users | Email recipient |
| `sender` | String(255) | NOT NULL | Sender email address |
| `receiver` | String(255) | NOT NULL | Receiver email address (alias) |
| `subject` | String(500) | NULLABLE | Email subject |
| `body_html` | Text | NULLABLE | HTML email body |
| `raw_content_link` | String(500) | NULLABLE | Link to raw email content |
| `timestamp` | DateTime | DEFAULT NOW | Email received time |

**Relationships:**
- Many-to-One with `User`

---

### 5. Transactions Table
Stores payment transactions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Transaction ID |
| `user_id` | BigInteger | FOREIGN KEY → Users | User making payment |
| `amount` | Integer | NOT NULL | Payment amount (MMK) |
| `plan_type` | String(50) | NOT NULL | Plan identifier |
| `receipt_photo_id` | String(255) | NOT NULL | Telegram photo file ID |
| `status` | Enum | DEFAULT 'pending' | pending/approved/rejected |
| `created_at` | DateTime | DEFAULT NOW | Transaction creation time |
| `updated_at` | DateTime | AUTO UPDATE | Last update time |

**Relationships:**
- Many-to-One with `User`

---

## Entity Relationship Diagram

```
┌─────────────┐
│    Users    │
│ (telegram_id)│
└──────┬──────┘
       │
       ├──────────┐
       │          │
       ▼          ▼
┌─────────────┐  ┌──────────────┐
│ UserEmails  │  │  EmailLogs   │
│    (id)     │  │     (id)     │
└──────┬──────┘  └──────────────┘
       │
       │
       ▼
┌─────────────┐
│   Domains   │
│    (id)     │
└─────────────┘

       ┌─────────────┐
       │Transactions │
       │    (id)     │
       └──────┬──────┘
              │
              ▼
       (Links to Users)
```

---

## Database Files

### Models (`database/models.py`)
- SQLAlchemy ORM models
- Type hints with `Mapped[]`
- Relationship definitions
- Enum for transaction status

### Database Connection (`database/database.py`)
- Async engine configuration
- Session management
- Database initialization
- Dependency injection helpers

### Package Init (`database/__init__.py`)
- Exports all models and utilities
- Single import point

---

## Usage Examples

### Initialize Database
```python
from database import init_db

# In async context
await init_db()
```

### Get Database Session
```python
from database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    # Your database operations
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### Create a User
```python
from database import User, AsyncSessionLocal

async with AsyncSessionLocal() as session:
    new_user = User(
        telegram_id=123456789,
        username="johndoe",
        first_name="John",
        last_name="Doe",
        credits=1
    )
    session.add(new_user)
    await session.commit()
```

### Query with Relationships
```python
from database import User, UserEmail, AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async with AsyncSessionLocal() as session:
    result = await session.execute(
        select(User)
        .options(selectinload(User.emails))
        .where(User.telegram_id == 123456789)
    )
    user = result.scalar_one_or_none()
    
    if user:
        print(f"User: {user.first_name}")
        for email in user.emails:
            print(f"  - {email.email_address}")
```

---

## Database Location

**File:** `email2telegram.db` (in project root)

**WAL Mode:** Enabled for better concurrency
- Creates `email2telegram.db-wal` (write-ahead log)
- Creates `email2telegram.db-shm` (shared memory)

---

## Migration Strategy

Currently using **direct table creation** via SQLAlchemy.

For future migrations, consider:
- **Alembic** for version-controlled migrations
- Backup before schema changes
- Test migrations on copy of production data

---

## Best Practices

1. **Always use async/await** with database operations
2. **Use context managers** for sessions
3. **Handle exceptions** and rollback on errors
4. **Close sessions** properly
5. **Use relationships** instead of manual joins
6. **Index frequently queried columns** (future optimization)

---

## Performance Considerations

- SQLite is suitable for small to medium scale
- For high traffic, consider PostgreSQL
- Current setup supports ~100 concurrent users
- WAL mode improves read/write concurrency

---

## Backup Recommendations

```bash
# Simple backup
cp email2telegram.db email2telegram.db.backup

# With timestamp
cp email2telegram.db "email2telegram.db.$(date +%Y%m%d_%H%M%S).backup"
```

Set up automated backups for production use.
