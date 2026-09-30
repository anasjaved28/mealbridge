from functools import wraps
from datetime import datetime, timezone
from flask import abort, redirect, url_for, flash
from flask_login import current_user
from app.models import utc_now, ROLE_RECEIVER


def role_required(*roles):
    """
    Decorator restricting route access to specific user roles.
    Redirects unapproved receivers to the pending page.
    """
    def decorator(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))

            if current_user.role not in roles:
                abort(403)

            # If user is a receiver and not approved yet, redirect to pending approval page
            # (unless they are already accessing the pending approval route or logging out)
            if current_user.role == ROLE_RECEIVER and not current_user.is_approved:
                # We let them access the pending page, but not protected receiver actions like feed/claim
                from flask import request
                if request.endpoint != "receiver.pending" and request.endpoint != "auth.logout":
                    flash("Your NGO account is currently awaiting administrative approval.", "info")
                    return redirect(url_for("receiver.pending"))

            return fn(*args, **kwargs)
        return decorated_view
    return decorator


def time_left(dt):
    """
    Calculate and format remaining time until best_before datetime.
    Returns strings like '2h 15m', '45m', '< 1m', or 'Expired'.
    """
    if not dt:
        return ""

    now = utc_now()
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    diff = dt - now
    total_seconds = int(diff.total_seconds())

    if total_seconds <= 0:
        return "Expired"

    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if hours > 24:
        days = hours // 24
        return f"{days}d {hours % 24}h"
    elif hours > 0:
        return f"{hours}h {minutes:02d}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "< 1m"


def clean_phone(phone_str):
    """
    Sanitize a phone string to raw digits for wa.me WhatsApp links.
    e.g. '+91 98888 11111' -> '919888811111'
    """
    if not phone_str:
        return ""
    import re
    return re.sub(r"[^\d]", "", str(phone_str))

