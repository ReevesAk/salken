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



def test_product_change_page_shows_gallery_inline_with_thumbnails(admin_client, product):
    product.productgallery_set.create(image='store/products/a.png')

    response = admin_client.get(f'/secure-login/store/product/{product.id}/change/')

    assert response.status_code == 200
    assert b'productgallery_set-TOTAL_FORMS' in response.content
    assert b'<img src="/media/store/products/a.png"' in response.content
