"""Utility functions for leave management system."""
import logging
import datetime
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from leavesystem import settings
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


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

def send_account_creation_email(employee):
    """ Send an email to the employee when the account is created"""
    full_name = f"{employee.first_name} {employee.last_name}".strip()
    raw_password = getattr(employee, 'temporary_password', 'Your chosen password')
    
    html_content = render_to_string(
        'emails/email.html', {
            'user_name': full_name if full_name else employee.email,
            'email': employee.email,
            'password': raw_password,  # Use the raw password
        })
    
    message = EmailMultiAlternatives(
        subject='Welcome to the Leave Management System',
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[employee.email],
    )

    message.content_subtype = 'html'
    message.send()

    return JsonResponse({'message': 'Email sent successfully.'})

def send_password_reset_email(employee):
    """Send a password reset email to the employee."""
    token = default_token_generator.make_token(employee)
    uid = urlsafe_base64_encode(force_bytes(employee.pk))
    reset_link = f"{settings.FRONTEND_URL}/set-password/{uid}/{token}/"

    full_name = f"{employee.first_name} {employee.last_name}".strip()
    html_content = render_to_string(
        'emails/password_reset_email.html', {
            'user_name': full_name if full_name else employee.email,
            'reset_link': reset_link,
        })

    message = EmailMultiAlternatives(
        subject='Password Reset Request',
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[employee.email],
    )

    message.content_subtype = 'html'
    message.send()

    return JsonResponse({'message': 'Password reset email sent successfully.'})