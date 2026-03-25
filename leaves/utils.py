"""Utility functions for leave management system."""
import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def calculate_working_days(start_date, end_date):
    """Calculate the number of working days between two dates."""
    working_days = 0

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")
        return 0

    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:
            working_days += 1
        current_date += datetime.timedelta(days=1)
    return working_days

def generate_password_reset_link(employee):
    """Generate a password reset link for the given user."""
    token = default_token_generator.make_token(employee)
    uid = urlsafe_base64_encode(force_bytes(employee.pk))
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
    return reset_link

def send_welcome_email(employee):
    """Send a welcome email to the new employee with instructions to set their password."""
    reset_link = generate_password_reset_link(employee)
    subject = "Welcome to the Leave Management System"
    message = f"""" \
        Hi {employee.first_name},
        
        \n\nWelcome to the Team Impact University! 
        Your account has been created on the Leave Management System. 
        
        Please set your password using the following link to activate your account:
        \n\n{reset_link}\n\n

        The link will expire in 24 hours, so please set your password as soon as possible. 
        If you did not expect this email, please contact your administrator immediately.

        
        Best regards,
        \n Team Impact University.

        """
    send_mail(
        subject, 
        message, 
        settings.DEFAULT_FROM_EMAIL, 
        [employee.email],
        fail_silently=False
        )

def send_password_reset_email(employee, reset_link):
    """Send a password reset email to the employee."""
    subject = "Password Reset Request - Leave Management System"
    message = f"""\
        Hi {employee.first_name},
        
        \n\nYou have requested a password reset for your Leave Management System account.
        
        Please click the following link to reset your password:
        \n\n{reset_link}\n\n

        The link will expire in 24 hours. If you did not request this password reset, 
        please ignore this email and contact your administrator if you have any concerns.

        
        Best regards,
        \n Team Impact University.

        """
    send_mail(
        subject, 
        message, 
        settings.DEFAULT_FROM_EMAIL, 
        [employee.email],
        fail_silently=False
        )