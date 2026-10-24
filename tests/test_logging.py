import importlib

import salken.settings


def test_logging_sends_app_and_django_logs_to_console(monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'WARNING')
    try:
        settings = importlib.reload(salken.settings)
    finally:
        monkeypatch.undo()
        importlib.reload(salken.settings)

    assert settings.LOGGING['root'] == {'handlers': ['console'], 'level': 'WARNING'}
    assert settings.LOGGING['loggers']['django']['handlers'] == ['console']
