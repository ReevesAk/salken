import pytest
from django.conf import settings
from django.urls import reverse

from cart.models import CartItem

pytestmark = pytest.mark.django_db


def test_empty_cart_counts_zero(client):
    response = client.get(reverse('store'))

    assert response.context['cart_count'] == 0


def test_counts_quantities_in_session_cart(client, product, variations):
    add = reverse('add_to_cart', args=[product.id])
    client.post(add, {'color': 'red'})
    client.post(add, {'color': 'red'})
    client.post(add, {'color': 'blue'})

    response = client.get(reverse('store'))

    assert response.context['cart_count'] == 3


def test_counts_only_the_users_items(client, user, product):
    CartItem.objects.create(product=product, quantity=2, user=user)
    CartItem.objects.create(product=product, quantity=5, user=None)
    client.force_login(user)

    response = client.get(reverse('store'))

    assert response.context['cart_count'] == 2


def test_admin_pages_skip_the_cart_count(client):
    response = client.get(reverse('admin:login'))

    assert response.status_code == 200
    assert 'cart_count' not in response.context
    assert settings.SESSION_COOKIE_NAME not in response.cookies
