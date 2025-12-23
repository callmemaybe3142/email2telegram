"""
Database Models
SQLAlchemy ORM models for the Email2Telegram service
"""

from sqlalchemy import BigInteger, String, Integer, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
import enum


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class TransactionStatus(enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    """
    Users Table
    Stores Telegram user information and credit balance
    """
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    credits: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    emails: Mapped[List["UserEmail"]] = relationship("UserEmail", back_populates="user", cascade="all, delete-orphan")
    email_logs: Mapped[List["EmailLog"]] = relationship("EmailLog", back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username}, credits={self.credits})>"


class Domain(Base):
    """
    Domains Table
    Stores available email domains
    """
    __tablename__ = "domains"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    emails: Mapped[List["UserEmail"]] = relationship("UserEmail", back_populates="domain", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Domain(id={self.id}, domain_name={self.domain_name}, is_active={self.is_active})>"


class UserEmail(Base):
    """
    UserEmails Table
    Stores user email addresses (aliases)
    """
    __tablename__ = "user_emails"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    email_address: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    domain_id: Mapped[int] = mapped_column(Integer, ForeignKey("domains.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="emails")
    domain: Mapped["Domain"] = relationship("Domain", back_populates="emails")
    
    def __repr__(self):
        return f"<UserEmail(id={self.id}, email_address={self.email_address})>"


class EmailLog(Base):
    """
    EmailLogs Table
    Stores received email logs
    """
    __tablename__ = "email_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    receiver: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_content_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="email_logs")
    
    def __repr__(self):
        return f"<EmailLog(id={self.id}, sender={self.sender}, receiver={self.receiver})>"


class Transaction(Base):
    """
    Transactions Table
    Stores payment transactions
    """
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    plan_type: Mapped[str] = mapped_column(String(50), nullable=False)
    receipt_photo_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus),
        default=TransactionStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status.value})>"
