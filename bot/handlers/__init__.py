"""
Bot handlers package
Each handler is in its own file for easier debugging and maintenance
"""

from .start import start_command
from .credits import credits_command
from .add_email import add_email_command
from .my_emails import my_emails_command
from .help import help_command
from .payment import handle_payment_callback, handle_photo
from .admin import handle_admin_callback

__all__ = [
    'start_command',
    'credits_command',
    'add_email_command',
    'my_emails_command',
    'help_command',
    'handle_payment_callback',
    'handle_photo',
    'handle_admin_callback'
]
