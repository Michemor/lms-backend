import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee
from .utils import send_account_creation_email, leave_request_status_email, leave_request_notification_email, leave_request_submitted_email

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Employee)
def trigger_welcome_email(sender, instance, created, **kwargs):
    """Fallback signal to send a welcome email for users created without a password.

    The main API creation flow always sets a password and explicitly sends the
    welcome email in the view; this signal is only for any other creation paths
    that might create an Employee without a password.
    """
    if created and not instance.password:
        try:
            send_account_creation_email(instance)
            logger.info(
                f"Welcome email sent from post_save signal to {instance.email}."
            )
        except Exception as e:
            # Never let email issues abort the save transaction for this fallback path
            logger.error(
                f"Failed to send welcome email from post_save signal to {instance.email}: {e}"
            )


#@receiver(post_save, sender=Employee)
#def trigger_leave_request_email(sender, instance, created, **kwargs):
#    """Send an email when a new leave request is created."""
#    if created and instance.leave_requests.exists():
#        try:
#            leave_request_submitted_email(instance)
#            leave_request_notification_email(instance)
#            logger.info(
#                f"Leave request email sent from post_save signal to {instance.email}."
#            )
#        except Exception as e:
#            logger.error(
#                f"Failed to send leave request email from post_save signal to {instance.email}: {e}"
#            )



# @receiver(post_save, sender=Employee)
# def trigger_leave_request_email_on_update(sender, instance, created, **kwargs):
#     """Send an email when a leave request is updated."""
#     if not created and instance.leave_requests.exists():
#         try:
#             leave_request_status_email(instance, instance.leave_requests.last(), 'update')
#             logger.info(
#                 f"Leave request update email sent from post_save signal to {instance.email}."
#             )
#         except Exception as e:
#             logger.error(
#                 f"Failed to send leave request update email from post_save signal to {instance.email}: {e}"
#             )
# 
# @receiver(post_save, sender=Employee)
# def trigger_leave_request_email_on_delete(sender, instance, created, **kwargs):
#     """Send an email when a leave request is deleted."""
#     if not created and instance.leave_requests.exists():
#         try:
#             leave_request_status_email(instance, instance.leave_requests.last(), 'cancellation')
#             logger.info(
#                 f"Leave request deletion email sent from post_save signal to {instance.email}."
#             )
#         except Exception as e:
#             logger.error(
#                 f"Failed to send leave request deletion email from post_save signal to {instance.email}: {e}"
#             )