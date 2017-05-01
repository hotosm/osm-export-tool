"""Functions for sending task-related emails."""
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_completion_notification(run):
    """Send a notification email to a user when their task finishes."""
    subject = u"Your OSM Export is ready: {}".format(run.job.name)
    from_email = 'OSM Export Tool <exports@hotosm.org>'

    ctx = {
        'url': 'http://{0}/exports/{1}'.format(settings.HOSTNAME, run.job.uid),
        'status': run.status,
    }

    text = get_template('email/email.txt').render(ctx)
    html = get_template('email/email.html').render(ctx)

    msg = EmailMultiAlternatives(
        subject,
        text,
        to=[run.user.email],
        from_email=from_email
    )
    msg.attach_alternative(html, "text/html")

    msg.send()


def send_hdx_completion_notification(run, region):
    """Send a notification email when an HDX task has completed."""
    if settings.HDX_NOTIFICATION_EMAIL:
        subject = u"HDX Task updated: {}".format(run.job.name)
        from_email = 'OSM Export Tool <exports@hotosm.org>'

        ctx = {
            'job': run.job,
            'region': region,
            'status': run.status,
            'url': 'http://{0}/exports/{1}'.format(
                settings.HOSTNAME, run.job.uid),
        }

        text = get_template('email/hdx_email.txt').render(ctx)

        msg = EmailMultiAlternatives(
            subject,
            text,
            to=[settings.HDX_NOTIFICATION_EMAIL],
            from_email=from_email
        )

        msg.send()


def send_hdx_error_notification(run, region):
    """Send a notification email when an HDX task has failed."""
    if settings.HDX_NOTIFICATION_EMAIL:
        subject = u"HDX Task has failed: {}".format(run.job.name)
        from_email = 'OSM Export Tool <exports@hotosm.org>'

        ctx = {
            'job': run.job,
            'region': region,
            'status': run.status,
            'url': 'http://{0}/exports/{1}'.format(
                settings.HOSTNAME, run.job.uid),
        }

        text = get_template('email/hdx_error_email.txt').render(ctx)

        msg = EmailMultiAlternatives(
            subject,
            text,
            to=[settings.HDX_NOTIFICATION_EMAIL],
            from_email=from_email
        )

        msg.send()


def send_error_notification(run):
    """Send a notification email to a user when their task fails."""
    subject = u"Your OSM Export has failed: {}".format(run.job.name)
    from_email = 'OSM Export Tool <exports@hotosm.org>'

    ctx = {
        'url': 'http://{0}/exports/{1}'.format(settings.HOSTNAME, run.job.uid),
        'status': run.status,
        'task_id': run.uid,
    }

    text = get_template('email/error_email.txt').render(ctx)
    html = get_template('email/error_email.html').render(ctx)

    msg = EmailMultiAlternatives(
        subject,
        text,
        to=[run.user.email],
        from_email=from_email
    )
    msg.attach_alternative(html, "text/html")

    msg.send()
