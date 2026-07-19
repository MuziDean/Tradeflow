"""
Email sending abstraction for TradeFlow.

Per SAD Section 10: Email provider must be swappable.
Use Django's email framework with provider-specific backends.
"""

from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    High-level email service for TradeFlow.

    Usage:
        email = EmailService()
        email.send_template(
            to="user@example.com",
            subject="Welcome",
            template="emails/welcome.html",
            context={"name": "John"}
        )
    """

    @staticmethod
    def send(to, subject, body, from_email=None, fail_silently=True):
        """Send a simple email."""
        if isinstance(to, str):
            to = [to]
        return send_mail(subject, body, from_email, to, fail_silently=fail_silently)

    @staticmethod
    def send_template(to, subject, template, context=None, from_email=None):
        """
        Send an email using an HTML template.

        Args:
            to: Recipient email or list of emails
            subject: Email subject
            template: Path to template (e.g., "emails/welcome.html")
            context: Template context dictionary
            from_email: Sender email (uses DEFAULT_FROM_EMAIL if not provided)
        """
        if isinstance(to, str):
            to = [to]
        if context is None:
            context = {}

        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to,
        )
        email.attach_alternative(html_content, "text/html")
        return email.send()