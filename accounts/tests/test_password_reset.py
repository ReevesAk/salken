import re

import pytest
from django.contrib.messages import get_messages
from django.core import mail
from django.urls import reverse

pytestmark = pytest.mark.django_db


def request_reset(client, email):
    return client.post(reverse('forgotPassword'), {'email': email})


def reset_link_path(email_body):
    match = re.search(r'http://testserver(\S+)', email_body)
    assert match, email_body
    return match.group(1)


def test_forgot_password_page_renders(client):
    assert client.get(reverse('forgotPassword')).status_code == 200


def test_unknown_email_does_not_send_mail(client, db):
    response = request_reset(client, 'nobody@example.com')

    assert response['Location'] == reverse('forgotPassword')
    assert mail.outbox == []


def test_full_reset_flow(client, user):
    request_reset(client, user.email)
    assert len(mail.outbox) == 1
    link = reset_link_path(mail.outbox[0].body)
    assert link.startswith('/accounts/resetpassword_validate/')

    response = client.get(link)
    assert response['Location'] == reverse('resetPassword')
    assert client.get(reverse('resetPassword')).status_code == 200

    response = client.post(
        reverse('resetPassword'),
        {
            'password': 'brand-new-pass',
            'confirm_password': 'brand-new-pass',
        },
    )

    assert response['Location'] == reverse('login')
    user.refresh_from_db()
    assert user.check_password('brand-new-pass')
    assert 'uid' not in client.session


def test_invalid_token_is_rejected(client, user):
    request_reset(client, user.email)
    link = reset_link_path(mail.outbox[0].body)
    tampered = link.rstrip('/').rsplit('/', 1)[0] + '/bad-token/'

    response = client.get(tampered)

    assert response['Location'] == reverse('login')
    assert 'uid' not in client.session


def test_reset_without_validated_link_redirects(client, user, password):
    response = client.post(
        reverse('resetPassword'),
        {
            'password': 'brand-new-pass',
            'confirm_password': 'brand-new-pass',
        },
    )

    assert response['Location'] == reverse('forgotPassword')
    user.refresh_from_db()
    assert user.check_password(password)


def test_mismatched_passwords_are_rejected(client, user, password):
    session = client.session
    session['uid'] = str(user.pk)
    session.save()

    response = client.post(
        reverse('resetPassword'),
        {
            'password': 'brand-new-pass',
            'confirm_password': 'other',
        },
    )

    assert response['Location'] == reverse('resetPassword')
    user.refresh_from_db()
    assert user.check_password(password)


@pytest.mark.parametrize('data', [{}, {'email': ''}, {'email': 'not-an-email'}])
def test_forgot_password_rejects_invalid_email(client, user, data):
    response = client.post(reverse('forgotPassword'), data)

    assert response.status_code == 302
    assert response['Location'] == reverse('forgotPassword')
    assert mail.outbox == []


def start_reset(client, user):
    session = client.session
    session['uid'] = str(user.pk)
    session.save()


def reset_messages(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


@pytest.mark.parametrize(
    'new_password, message',
    [
        ('short', 'This password is too short. It must contain at least 8 characters.'),
        ('84629173501', 'This password is entirely numeric.'),
        ('password123', 'This password is too common.'),
    ],
)
def test_reset_enforces_password_validators(
    client, user, password, new_password, message
):
    start_reset(client, user)

    response = client.post(
        reverse('resetPassword'),
        {'password': new_password, 'confirm_password': new_password},
    )

    assert response['Location'] == reverse('resetPassword')
    assert message in reset_messages(response)
    user.refresh_from_db()
    assert user.check_password(password)


def test_reset_with_missing_fields_redirects_back(client, user):
    start_reset(client, user)

    response = client.post(reverse('resetPassword'), {})

    assert response['Location'] == reverse('resetPassword')


def test_reset_for_deleted_account_redirects_to_forgot_password(client, user):
    start_reset(client, user)
    user.delete()

    response = client.post(
        reverse('resetPassword'),
        {'password': 'brand-new-pass', 'confirm_password': 'brand-new-pass'},
    )

    assert response['Location'] == reverse('forgotPassword')
