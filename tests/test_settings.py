import importlib
import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured

import salken.settings


@pytest.fixture
def reload_settings(monkeypatch):
    def reload(**env):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return importlib.reload(salken.settings)

    yield reload
    monkeypatch.undo()
    importlib.reload(salken.settings)


def test_local_settings_use_filesystem_static_files(reload_settings, monkeypatch):
    monkeypatch.delenv('AWS_STORAGE_BUCKET_NAME', raising=False)

    settings = reload_settings()

    assert settings.STATIC_URL == '/static/'
    assert not hasattr(settings, 'STORAGES')


def test_bucket_enables_s3_static_storage(reload_settings):
    settings = reload_settings(
        AWS_STORAGE_BUCKET_NAME='salken-assets',
        AWS_ACCESS_KEY_ID='key',
        AWS_SECRET_ACCESS_KEY='secret',
    )

    assert settings.STORAGES['staticfiles']['BACKEND'] == (
        'storages.backends.s3boto3.S3Boto3Storage'
    )
    assert settings.STATIC_URL == 'https://salken-assets.s3.amazonaws.com/static/'


def test_debug_off_requires_secret_key(reload_settings, monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)

    with pytest.raises(ImproperlyConfigured, match='SECRET_KEY'):
        reload_settings(DEBUG='False')


def test_debug_on_falls_back_to_development_key(reload_settings, monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)

    settings = reload_settings(DEBUG='True')

    assert settings.SECRET_KEY.startswith('django-insecure-')


def test_https_enables_secure_cookies_and_redirect(reload_settings):
    settings = reload_settings(HTTPS='True')

    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SECURE_HSTS_SECONDS == 3600
    assert settings.SECURE_PROXY_SSL_HEADER == ('HTTP_X_FORWARDED_PROTO', 'https')


def test_production_configuration_passes_deploy_checks():
    env = {
        **os.environ,
        'DEBUG': 'False',
        'HTTPS': 'True',
        'SECRET_KEY': secrets.token_urlsafe(50),
    }

    result = subprocess.run(
        [sys.executable, 'manage.py', 'check', '--deploy', '--fail-level', 'WARNING'],
        cwd=Path(__file__).resolve().parent.parent,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
