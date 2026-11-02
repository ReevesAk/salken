import re

import pytest
from django.core import mail
from django.urls import reverse

from accounts.models import Account, UserProfile

pytestmark = pytest.mark.django_db


def registration_data(**overrides):
    data = {
        'first_name': 'Ada',
        'last_name': 'Lovelace',
        'phone_no': '5550100',
        'email': 'ada@example.com',
        'password': 'analytical-engine-1843',
        'confirm_password': 'analytical-engine-1843',
    }
    data.update(overrides)
    return data


def test_register_page_renders(client):
    response = client.get(reverse('register'))

    assert response.status_code == 200
    assert 'form' in response.context


def test_register_creates_inactive_account_and_profile(client):
    response = client.post(reverse('register'), registration_data())

    assert response.status_code == 302
    assert (
        response['Location']
        == '/accounts/login/?command=verification&email=ada@example.com'
    )

    user = Account.objects.get(email='ada@example.com')
    assert user.username == 'AdaLovelace'
    assert user.phone_no == '5550100'
    assert user.is_active is False
    assert user.check_password('analytical-engine-1843')
    assert UserProfile.objects.filter(user=user).exists()


def test_register_sends_activation_email(client):
    client.post(reverse('register'), registration_data())

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['ada@example.com']
    assert '/accounts/activate/' in mail.outbox[0].body


def test_register_rejects_mismatched_passwords(client):
    response = client.post(
        reverse('register'), registration_data(confirm_password='something-else')
    )

    assert response.status_code == 200
    assert not Account.objects.exists()


def activation_path(email_body):
    return re.search(r'http://testserver(\S+)', email_body).group(1)


def test_activation_link_activates_account(client):
    client.post(reverse('register'), registration_data())

    response = client.get(activation_path(mail.outbox[0].body))

    assert response['Location'] == reverse('login')
    assert Account.objects.get(email='ada@example.com').is_active is True


def test_tampered_activation_link_is_rejected(client):
    client.post(reverse('register'), registration_data())
    path = activation_path(mail.outbox[0].body).rstrip('/').rsplit('/', 1)[0]

    response = client.get(path + '/bad-token/')

    assert response['Location'] == reverse('register')
    assert Account.objects.get(email='ada@example.com').is_active is False


def test_inactive_account_cannot_log_in(client):
    client.post(reverse('register'), registration_data())

    client.post(
        reverse('login'),
        {
            'email': 'ada@example.com',
            'password': 'analytical-engine-1843',
        },
    )

    assert '_auth_user_id' not in client.session


def test_second_person_with_same_name_can_register(client):
    client.post(reverse('register'), registration_data())

    response = client.post(
        reverse('register'),
        registration_data(email='ada2@example.com', phone_no='5550101'),
    )

    assert response.status_code == 302
    assert Account.objects.filter(first_name='Ada', last_name='Lovelace').count() == 2


@pytest.mark.parametrize(
    'password, error',
    [
        (
            'short1',
            'This password is too short. It must contain at least 8 characters.',
        ),
        ('password123', 'This password is too common.'),
        ('lovelace-ada', 'The password is too similar to the last name.'),
    ],
)
def test_register_enforces_password_validators(client, password, error):
    response = client.post(
        reverse('register'),
        registration_data(password=password, confirm_password=password),
    )

    assert response.status_code == 200
    assert error in response.context['form'].errors['password']
    assert not Account.objects.exists()


@pytest.mark.parametrize(
    'field, value', [('email', 'ada@example.com'), ('phone_no', '5550100')]
)
def test_register_rejects_duplicate_email_and_phone(client, field, value):
    client.post(reverse('register'), registration_data())

    response = client.post(
        reverse('register'),
        registration_data(
            **{'email': 'other@example.com', 'phone_no': '5550199', field: value}
        ),
    )

    assert response.status_code == 200
    assert field in response.context['form'].errors
    assert Account.objects.count() == 1
