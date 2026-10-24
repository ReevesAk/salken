import importlib

import pytest

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

