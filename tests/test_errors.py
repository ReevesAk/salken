import importlib
from unittest import mock

from sentry_sdk.integrations.django import DjangoIntegration

import salken.settings
from salken.errors import init_error_tracking


def test_no_dsn_disables_error_tracking():
    with mock.patch('salken.errors.sentry_sdk.init') as init:
        assert init_error_tracking(dsn='', environment='production') is False

    init.assert_not_called()


def test_dsn_initializes_sentry_without_personal_data():
    with mock.patch('salken.errors.sentry_sdk.init') as init:
        enabled = init_error_tracking(
            dsn='https://key@sentry.example/1',
            environment='production',
            traces_sample_rate=0.1,
        )

    assert enabled is True
    kwargs = init.call_args.kwargs
    assert kwargs['dsn'] == 'https://key@sentry.example/1'
    assert kwargs['environment'] == 'production'
    assert kwargs['traces_sample_rate'] == 0.1
    assert kwargs['send_default_pii'] is False
    assert any(isinstance(i, DjangoIntegration) for i in kwargs['integrations'])


def test_settings_enable_sentry_from_environment(monkeypatch):
    monkeypatch.setenv('SENTRY_DSN', 'https://key@sentry.example/1')
    monkeypatch.setenv('SENTRY_ENVIRONMENT', 'staging')
    try:
        with mock.patch('salken.errors.sentry_sdk.init') as init:
            importlib.reload(salken.settings)
    finally:
        monkeypatch.undo()
        importlib.reload(salken.settings)

    assert init.call_args.kwargs['dsn'] == 'https://key@sentry.example/1'
    assert init.call_args.kwargs['environment'] == 'staging'
