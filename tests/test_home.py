import pytest
from django.urls import reverse

from store.models import Product

pytestmark = pytest.mark.django_db


def test_home_lists_available_products(client, product):
    Product.objects.create(
        product_name='Retired Shirt',
        slug='retired-shirt',
        price=10,
        image='photos/products/retired.jpg',
        stock=0,
        is_available=False,
        category=product.category,
    )

    response = client.get(reverse('home'))

    assert response.status_code == 200
    assert list(response.context['products']) == [product]
    assert product.get_url().encode() in response.content


def test_home_renders_without_products(client, db):
    assert client.get(reverse('home')).status_code == 200
