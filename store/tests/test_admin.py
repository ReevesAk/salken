import pytest

from accounts.models import Account

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    admin = Account.objects.create_superuser(
        first_name='Grace', last_name='Hopper', email='grace@example.com',
        username='GraceHopper', password='cobol-1959',
    )
    client.force_login(admin)
    return client


@pytest.mark.parametrize('model', ['product', 'variation', 'reviewrating', 'productgallery'])
def test_store_admin_changelists_render(admin_client, product, variations, model):
    response = admin_client.get(f'/secure-login/store/{model}/')

    assert response.status_code == 200

