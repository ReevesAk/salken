import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PIN = re.compile(r'^([A-Za-z0-9._-]+)==([^\s;]+)')


def normalize(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def read_pins(path):
    pins = {}
    for line in (ROOT / path).read_text().splitlines():
        match = PIN.match(line.strip())
        if match:
            pins[normalize(match.group(1))] = match.group(2)
    return pins


LOCKED = read_pins('requirements.lock')


@pytest.mark.parametrize('path', ['requirements.txt', 'requirements-dev.txt'])
def test_direct_pins_match_lockfile(path):
    mismatched = {
        name: (version, LOCKED.get(name))
        for name, version in read_pins(path).items()
        if LOCKED.get(name) != version
    }

    assert not mismatched, (
        f'{path} and requirements.lock disagree (pinned, locked): {mismatched}. '
        'Regenerate the lock with the command in README.md.'
    )
