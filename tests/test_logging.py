import importlib

import salken.settings


def test_logging_sends_app_and_django_logs_to_console(monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'WARNING')
    try:
        logging_config = importlib.reload(salken.settings).LOGGING
    finally:
        monkeypatch.undo()
        importlib.reload(salken.settings)

    assert logging_config['root'] == {'handlers': ['console'], 'level': 'WARNING'}
    assert logging_config['loggers']['django']['handlers'] == ['console']
