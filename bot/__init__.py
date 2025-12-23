"""
Bot package initialization
"""

from .bot import create_bot_application, send_email_notification
from .handlers import *

__all__ = ['create_bot_application', 'send_email_notification']
