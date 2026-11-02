import pytest

from accounts.forms import LoginForm, PasswordResetRequestForm


def test_login_form_accepts_valid_credentials():
    form = LoginForm({'email': 'ada@example.com', 'password': ' secret '})

    assert form.is_valid()
    assert form.cleaned_data['password'] == ' secret '


@pytest.mark.parametrize('email', ['', 'not-an-email', 'ada@', '@example.com'])
def test_login_form_rejects_malformed_email(email):
    form = LoginForm({'email': email, 'password': 'secret'})

    assert not form.is_valid()
    assert 'email' in form.errors


def test_login_form_requires_password():
    form = LoginForm({'email': 'ada@example.com'})

    assert not form.is_valid()
    assert 'password' in form.errors


@pytest.mark.parametrize('email', ['', 'not-an-email', 'ada@'])
def test_password_reset_request_form_rejects_invalid_email(email):
    form = PasswordResetRequestForm({'email': email})

    assert not form.is_valid()
    assert 'email' in form.errors
