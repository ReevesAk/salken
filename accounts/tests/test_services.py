import smtplib
from unittest import mock

import pytest
from django.core import mail
from django.urls import reverse

from accounts.models import Account, UserProfile
from accounts.services import AccountRegistrationError, register_user

pytestmark = pytest.mark.django_db

SEND = 'django.core.mail.EmailMessage.send'


def register(**overrides):
    details = {
        'first_name': 'Ada',
        'last_name': 'Lovelace',
        'phone_no': '5550100',
        'email': 'ada@example.com',
        'password': 'analytical-engine-1843',
        'domain': 'shop.example',
        **overrides,
    }
    return register_user(**details)


class TestRegisterUser:
    def test_creates_inactive_account_with_profile(self):
        user = register()

        assert user.is_active is False
        assert user.phone_no == '5550100'
        assert user.check_password('analytical-engine-1843')
        profile = UserProfile.objects.get(user=user)
        assert profile.profile_picture.name == 'default/default-user.png'

    def test_emails_activation_link(self):
        user = register()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
        assert 'http://shop.example/accounts/activate/' in mail.outbox[0].body

    @pytest.mark.parametrize(
        'failure', [smtplib.SMTPException('refused'), ConnectionRefusedError()]
    )
    def test_email_failure_saves_nothing(self, failure):
        with mock.patch(SEND, side_effect=failure):
            with pytest.raises(AccountRegistrationError):
                register()

        assert not Account.objects.exists()
        assert not UserProfile.objects.exists()

    def test_can_register_again_after_email_failure(self):
        with mock.patch(SEND, side_effect=smtplib.SMTPException('refused')):
            with pytest.raises(AccountRegistrationError):
                register()

        user = register()

        assert user.email == 'ada@example.com'


def test_register_view_shows_email_failure_on_form(client):
    with mock.patch(SEND, side_effect=smtplib.SMTPException('refused')):
        response = client.post(
            reverse('register'),
            {
                'first_name': 'Ada',
                'last_name': 'Lovelace',
                'phone_no': '5550100',
                'email': 'ada@example.com',
                'password': 'analytical-engine-1843',
                'confirm_password': 'analytical-engine-1843',
            },
        )

    assert response.status_code == 200
    assert response.context['form'].non_field_errors() == [
        "We couldn't send your activation email. Please try again later."
    ]
    assert not Account.objects.exists()


class TestUsernames:
    def test_username_joins_first_and_last_name(self):
        assert register().username == 'AdaLovelace'

    def test_same_name_gets_a_unique_username(self):
        first = register()
        second = register(email='ada2@example.com', phone_no='5550101')
        third = register(email='ada3@example.com', phone_no='5550102')

        assert first.username == 'AdaLovelace'
        assert second.username == 'AdaLovelace2'
        assert third.username == 'AdaLovelace3'

    def test_username_fits_the_field(self):
        user = register(first_name='A' * 50, last_name='B' * 50)

        # Account.username has max_length=50.
        assert user.username == 'A' * 50
