import logging
import threading

from coffin.template.loader import render_to_string
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage
from djcelery import celery
from jinja2.exceptions import TemplateError


# Thread-specific context
# -----------------------

# As long as we don't use other concurrency scheme than threading
# (e.g. greenlet), just using `threading.Local` should be fine.
_local = threading.local()


class NoEmailContext(object):
    def __enter__(self):
        _local.email_enabled = False

    def __exit__(self, type, value, traceback):
        _local.email_enabled = True


# Email Sender
# ------------

class EmailException(Exception):
    pass


logger = logging.getLogger(__name__)

default_mail_context = {
    'settings': settings,
}


@celery.task
def _send_email(template, recipients, context=None):
    if isinstance(recipients, basestring):
        recipients = [recipients]

    mail_context = default_mail_context.copy()
    mail_context.update(context or {})

    try:
        rendered = render_to_string(template, mail_context).strip()
    except TemplateError as e:
        logger.error('Failed to render "{0}" mail for {1}: {2}'.format(
            template, u', '.join(recipients), e))
        raise EmailException(e)

    subject, message = [token.strip() for token in rendered.split(
        settings.EMAIL_DELIMITER)]
    subject = subject.replace('\n', '')

    from_email = settings.CONTACT_EMAIL

    msgs = []
    for recipient in recipients:
        msg = EmailMessage(subject, message, from_email=from_email,
                           to=[recipient])
        msg.content_subtype = {'txt': 'plain', 'html': 'html'}.get(
            template.split('.')[-1], 'plain')
        msgs.append(msg)

    try:
        connection = mail.get_connection()
        connection.send_messages(msgs)
        connection.close()
    except Exception as e:
        logger.error('Failed to send "{0}" mail for {1}: {2}'.format(
            template, u', '.join(recipients), e))
        raise EmailException(e)

    logger.info('Successfully sent "{0}" mail to {1} recipient(s): {2}'.format(
        template, len(msgs), u', '.join(recipients)))


def send_email(template, recipients, context=None, async=True):
    if not getattr(_local, 'email_enabled', True):
        return

    if settings.DEBUG:
        if isinstance(recipients, basestring):
            recipients = [recipients]
        recipients = [email for email in recipients
                      if email in settings.ALLOWED_DEBUG_EMAIL]
        if not recipients:
            logger.warn('No recipients to send due to debug setting')
            return

    if not settings.DEBUG and async:
        return _send_email.delay(template, recipients, context)
    else:
        return _send_email(template, recipients, context)


# Utility
# -------

def get_email_domain(email):
    return email.split('@')[-1]
