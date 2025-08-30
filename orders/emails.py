from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .pdf_utils import build_order_pdf


def _to_address(order):
    # prefer order.email snapshot, fallback to user email
    return order.email or (order.user.email if order.user else None)


def send_order_pending_email(order):
    """
    Sent right after checkout – status likely 'new' or 'pending'.
    PDF: order summary (no address required if you prefer).
    """
    to_email = _to_address(order)
    if not to_email:
        return  # nothing to send to

    subject = f"[{settings.SITE_NAME}] Order #{order.id} received"
    context = {
        "order": order,
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
    }

    text_body = render_to_string("orders/emails/pending.txt", context)
    html_body = render_to_string("orders/emails/pending.html", context)

    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [to_email])
    msg.attach_alternative(html_body, "text/html")

    # attach PDF (no address block necessary if you prefer)
    pdf = build_order_pdf(order, title="Order Confirmation", include_address=False, show_status=True)
    filename = f"order_{order.id}_confirmation.pdf"
    msg.attach(filename, pdf.read(), "application/pdf")

    msg.send(fail_silently=False)


def send_order_paid_email(order):
    """
    Sent when Stripe payment is confirmed (webhook).
    PDF: includes shipping address and shows 'Paid' status.
    """
    to_email = _to_address(order)
    if not to_email:
        return

    subject = f"[{settings.SITE_NAME}] Payment confirmed for Order #{order.reference}"
    context = {
        "order": order,
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
    }

    text_body = render_to_string("orders/emails/paid.txt", context)
    html_body = render_to_string("orders/emails/paid.html", context)

    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [to_email])
    msg.attach_alternative(html_body, "text/html")

    pdf = build_order_pdf(order, title="Paid Order Summary", include_address=True, show_status=True)
    filename = f"order_{order.reference}_paid.pdf"
    msg.attach(filename, pdf.read(), "application/pdf")

    msg.send(fail_silently=False)
