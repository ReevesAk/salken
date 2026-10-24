import importlib

import decouple
import pytest

import salken.settings

RDS_VARS = ['RDS_DB_NAME', 'RDS_USERNAME', 'RDS_PASSWORD', 'RDS_HOSTNAME', 'RDS_PORT']


@pytest.fixture
def settings_from_env_file(monkeypatch, tmp_path):
    """Reload settings with a .env file in tmp_path and no RDS_* environment."""
    for name in RDS_VARS:
        monkeypatch.delenv(name, raising=False)

    def load(env_file_text):
        (tmp_path / '.env').write_text(env_file_text)
        monkeypatch.setattr(
            decouple, 'config', decouple.AutoConfig(search_path=tmp_path)
        )
        return importlib.reload(salken.settings).DATABASES['default']

    yield load
    monkeypatch.undo()
    importlib.reload(salken.settings)


def test_env_file_configures_postgres(settings_from_env_file):
    database = settings_from_env_file(
        'RDS_DB_NAME=salken\n'
        'RDS_USERNAME=salken\n'
        'RDS_PASSWORD=secret\n'
        'RDS_HOSTNAME=db.internal\n'
        'RDS_PORT=6543\n'
    )

    assert database['ENGINE'] == 'django.db.backends.postgresql'
    assert (database['NAME'], database['USER'], database['PASSWORD']) == (
        'salken',
        'salken',
        'secret',
    )
    assert (database['HOST'], database['PORT']) == ('db.internal', '6543')


def test_postgres_host_and_port_have_defaults(settings_from_env_file):
    database = settings_from_env_file(
        'RDS_DB_NAME=salken\nRDS_USERNAME=salken\nRDS_PASSWORD=secret\n'
    )

    assert (database['HOST'], database['PORT']) == ('localhost', '5432')


def test_empty_database_name_uses_sqlite(settings_from_env_file):
    database = settings_from_env_file('RDS_DB_NAME=\nRDS_USERNAME=salken\n')

    assert database['ENGINE'] == 'django.db.backends.sqlite3'


def test_env_example_defaults_to_sqlite(settings_from_env_file):
    example = (salken.settings.BASE_DIR / '.env.example').read_text()

    assert settings_from_env_file(example)['ENGINE'] == 'django.db.backends.sqlite3'


def test_env_example_lists_every_database_variable():
    example = (salken.settings.BASE_DIR / '.env.example').read_text()
    defined = {line.split('=', 1)[0] for line in example.splitlines() if '=' in line}

    assert set(RDS_VARS) <= defined
