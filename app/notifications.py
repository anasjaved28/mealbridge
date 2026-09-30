import logging
from flask import current_app
from flask_mail import Message
from app.extensions import mail

logger = logging.getLogger(__name__)


def send_email_notification(subject: str, recipients: list, body: str, html_body: str = None) -> bool:
    """
    Safely sends an email via Flask-Mail.
    Catches exceptions so notification delivery failures never crash the user request.
    """
    if not recipients:
        return False

    recipients_list = recipients if isinstance(recipients, (list, tuple)) else [recipients]
    sender = current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@mealbridge.org")

    try:
        msg = Message(
            subject=f"[MealBridge] {subject}",
            recipients=recipients_list,
            body=body,
            html=html_body,
            sender=sender,
        )
        mail.send(msg)
        logger.info(f"Email sent to {recipients_list}: {subject}")
        return True
    except Exception as exc:
        logger.warning(f"Failed to send email to {recipients_list} ({exc}). Skipping notification.")
        return False


def notify_receiver_approved(receiver) -> bool:
    """Notifies an NGO receiver when their organization account is approved by admin."""
    if not receiver or not receiver.email:
        return False

    subject = "Account Approved - Welcome to MealBridge!"
    body = (
        f"Hi {receiver.name},\n\n"
        f"Great news! Your NGO receiver account has been approved by the platform administrator.\n\n"
        f"You can now log in, view available surplus food in {receiver.city}, and claim meals for immediate pickup:\n"
        f"https://mealbridge.org/receiver/feed\n\n"
        f"Thank you for joining our mission to eliminate food waste and feed communities!\n\n"
        f"— The MealBridge Team"
    )
    return send_email_notification(subject, receiver.email, body)


def notify_donor_listing_claimed(listing) -> bool:
    """Notifies a donor when their surplus food listing has been claimed by an NGO."""
    if not listing or not listing.donor or not listing.donor.email:
        return False

    ngo_name = listing.claimed_by.name if listing.claimed_by else "A verified NGO"
    subject = f"Your Food Listing Was Claimed! ({listing.food_name})"
    body = (
        f"Hi {listing.donor.name},\n\n"
        f"{ngo_name} has just claimed your donation of {listing.quantity} plates of {listing.food_name}!\n\n"
        f"Pickup Location: {listing.address}, {listing.city}\n"
        f"Handover PIN: {listing.pickup_pin or 'N/A'}\n\n"
        f"The pickup driver will provide this 4-digit PIN upon arrival. "
        f"Please verify the PIN on your MealBridge dashboard to confirm dispatch.\n\n"
        f"— The MealBridge Team"
    )
    return send_email_notification(subject, listing.donor.email, body)


def notify_receiver_food_dispatched(listing) -> bool:
    """Notifies the NGO when the donor kitchen has marked the food as dispatched."""
    if not listing or not listing.claimed_by or not listing.claimed_by.email:
        return False

    subject = f"Food Dispatched - {listing.food_name}"
    body = (
        f"Hi {listing.claimed_by.name},\n\n"
        f"{listing.donor.name} has dispatched your claimed food ({listing.quantity} plates of {listing.food_name}).\n\n"
        f"Once you receive the food, please mark it as 'Collected' in your MealBridge dashboard to close the loop.\n\n"
        f"— The MealBridge Team"
    )
    return send_email_notification(subject, listing.claimed_by.email, body)


def notify_donor_food_collected(listing) -> bool:
    """Notifies the donor when the receiver has confirmed receipt and collection."""
    if not listing or not listing.donor or not listing.donor.email:
        return False

    subject = f"Donation Completed! - {listing.food_name}"
    body = (
        f"Hi {listing.donor.name},\n\n"
        f"{listing.claimed_by.name} has successfully collected {listing.quantity} plates of {listing.food_name}!\n\n"
        f"Your CSR / Tax Donation Certificate is now generated and ready to download on your dashboard.\n\n"
        f"Thank you for making a real difference!\n\n"
        f"— The MealBridge Team"
    )
    return send_email_notification(subject, listing.donor.email, body)
