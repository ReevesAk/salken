import decouple
import pytest


@pytest.fixture
def ignore_env_file(monkeypatch, tmp_path):
    """Make settings ignore the developer's .env, so only os.environ applies.

    The README has developers copy .env.example to .env, whose values would
    otherwise override what a test sets up. Undone by monkeypatch.undo().
    """
    monkeypatch.setattr(decouple, 'config', decouple.AutoConfig(search_path=tmp_path))
