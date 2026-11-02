import logging
import smtplib

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Account, UserProfile

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_PICTURE = 'default/default-user.png'


class AccountRegistrationError(Exception):
    """Registration could not be completed; nothing was saved."""


# register_user creates an inactive account with its profile and emails the
# activation link. It runs in one transaction, so if the email can't be sent
# no account is left behind and the person can simply try again.
def register_user(*, first_name, last_name, phone_no, email, password, domain):
    try:
        with transaction.atomic():
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=_unique_username(first_name + last_name),
                email=email,
                password=password,
            )
            user.phone_no = phone_no
            user.save()
            UserProfile.objects.create(
                user=user, profile_picture=DEFAULT_PROFILE_PICTURE
            )
            send_activation_email(user, domain)
    except (smtplib.SMTPException, OSError) as error:
        logger.exception('Could not send activation email to %s', email)
        raise AccountRegistrationError(
            "We couldn't send your activation email. Please try again later."
        ) from error
    return user


# _unique_username returns base, or base with the lowest numeric suffix that
# isn't taken, truncated to fit Account.username.
def _unique_username(base):
    max_length = Account._meta.get_field('username').max_length
    candidate = base[:max_length]
    suffix = 1
    while Account.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = base[: max_length - len(str(suffix))] + str(suffix)
    return candidate


# send_activation_email emails the user a one-time link to activate their
# account.
def send_activation_email(user, domain):
    message = render_to_string(
        'accounts/account_verification_email.html',
        {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        },
    )
    EmailMessage(
        'Follow the link to activate your account', message, to=[user.email]
    ).send()
