import importlib
import json
import logging.config
from unittest import mock

import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError

import salken.settings


@pytest.fixture
def load_settings(monkeypatch):
    """Reload salken.settings under the given environment variables."""

    def load(**env):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return importlib.reload(salken.settings)

    yield load
    monkeypatch.undo()
    importlib.reload(salken.settings)


def test_logging_sends_app_and_django_logs_to_stdout(load_settings):
    logging_config = load_settings(LOG_LEVEL='WARNING').LOGGING

    assert logging_config['root'] == {'handlers': ['console'], 'level': 'WARNING'}
    assert logging_config['loggers']['django']['handlers'] == ['console']
    assert logging_config['handlers']['console']['stream'] == 'ext://sys.stdout'


def test_text_format_is_the_default_locally(load_settings):
    settings = load_settings(DEBUG='True')

    assert settings.LOG_FORMAT == 'text'


def test_json_format_is_the_default_in_production(load_settings):
    settings = load_settings(DEBUG='False', SECRET_KEY='x' * 50)

    assert settings.LOGGING['handlers']['console']['formatter'] == 'json'


def test_unknown_log_format_is_rejected(load_settings):
    with pytest.raises(ImproperlyConfigured, match='LOG_FORMAT'):
        load_settings(LOG_FORMAT='xml')


@pytest.mark.django_db
def test_request_logs_are_emitted_as_json(load_settings, client, capsys):
    logging_config = load_settings(LOG_FORMAT='json').LOGGING
    logging.config.dictConfig(logging_config)
    try:
        with mock.patch(
            'salken.health.connection.cursor', side_effect=OperationalError('down')
        ):
            response = client.get('/health/')
    finally:
        logging.config.dictConfig(django_settings.LOGGING)

    assert response.status_code == 503
    lines = capsys.readouterr().out.splitlines()
    records = {
        r['logger']: r for r in (json.loads(line) for line in lines if line.strip())
    }

    health = records['salken.health']
    assert health['level'] == 'ERROR'
    assert health['message'] == 'Health check failed: database unavailable'
    assert 'OperationalError: down' in health['exc_info']
    assert 'time' in health
    # Django's own request logging uses the same format.
    assert records['django.request']['level'] == 'ERROR'
