import logging
from unittest import mock

import pytest
from django.db import OperationalError

pytestmark = pytest.mark.django_db


def test_health_reports_ok(client):
    response = client.get('/health/')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'database': 'ok'}


def test_health_accepts_unlisted_host(client):
    # Load balancers address health checks to the instance IP.
    response = client.get('/health/', HTTP_HOST='10.0.3.17')

    assert response.status_code == 200


def test_other_paths_still_validate_host(client):
    response = client.get('/', HTTP_HOST='10.0.3.17')

    assert response.status_code == 400


def test_health_reports_database_failure(client, caplog):
    with mock.patch(
        'salken.health.connection.cursor', side_effect=OperationalError('down')
    ):
        with caplog.at_level(logging.ERROR, logger='salken.health'):
            response = client.get('/health/')

    assert response.status_code == 503
    assert response.json() == {'status': 'error', 'database': 'unavailable'}
    assert 'database unavailable' in caplog.text
