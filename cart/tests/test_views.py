import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory
from django.urls import reverse

from cart.models import Cart, CartItem
from cart.views import _cart_id, _resolve_variations

pytestmark = pytest.mark.django_db


def add_to_cart(client, product, **variations):
    return client.post(reverse('add_to_cart', args=[product.id]), variations)


class TestResolveVariations:
    def test_matches_posted_variations_case_insensitively(self, product, variations):
        request = RequestFactory().post('/', {'color': 'RED', 'size': 'Large'})

        resolved = _resolve_variations(request, product)

        assert set(resolved) == {variations['red'], variations['large']}

    def test_ignores_unknown_keys_and_values(self, product, variations):
        request = RequestFactory().post(
            '/', {'csrfmiddlewaretoken': 'x', 'color': 'green'}
        )

        assert _resolve_variations(request, product) == []

    def test_get_request_has_no_variations(self, product, variations):
        request = RequestFactory().get('/', {'color': 'red'})

        assert _resolve_variations(request, product) == []


class TestAddToCartAnonymous:
    def test_creates_session_cart_and_item(self, client, product, variations):
        response = add_to_cart(client, product, color='red')

        assert response.status_code == 302
        assert response['Location'] == reverse('cart')
        cart = Cart.objects.get(cart_id=client.session.session_key)
        item = CartItem.objects.get(cart=cart)
        assert item.user is None
        assert item.quantity == 1
        assert list(item.variation.all()) == [variations['red']]

    def test_same_variations_increment_quantity(self, client, product, variations):
        add_to_cart(client, product, color='red', size='large')
        add_to_cart(client, product, size='large', color='red')

        item = CartItem.objects.get()
        assert item.quantity == 2

    def test_different_variations_create_separate_items(
        self, client, product, variations
    ):
        add_to_cart(client, product, color='red')
        add_to_cart(client, product, color='blue')

        assert CartItem.objects.count() == 2
        assert all(item.quantity == 1 for item in CartItem.objects.all())

    def test_unknown_product_returns_404(self, client, db):
        response = client.post(reverse('add_to_cart', args=[999]))

        assert response.status_code == 404


class TestAddToCartAuthenticated:
    def test_creates_item_owned_by_user(self, client, user, product, variations):
        client.force_login(user)

        add_to_cart(client, product, color='red')

        item = CartItem.objects.get()
        assert item.user == user
        assert item.cart is None
        assert item.quantity == 1

    def test_same_variations_increment_quantity(
        self, client, user, product, variations
    ):
        client.force_login(user)

        add_to_cart(client, product, color='blue')
        add_to_cart(client, product, color='blue')
        add_to_cart(client, product, color='blue')

        assert CartItem.objects.get(user=user).quantity == 3

    def test_does_not_merge_with_another_users_items(
        self, client, user, product, variations
    ):
        CartItem.objects.create(product=product, quantity=5, user=None)
        client.force_login(user)

        add_to_cart(client, product)

        assert CartItem.objects.get(user=user).quantity == 1


class TestRemoveFromCart:
    def test_decrements_quantity(self, client, user, product):
        item = CartItem.objects.create(product=product, quantity=2, user=user)
        client.force_login(user)

        client.get(reverse('remove_from_cart', args=[product.id, item.id]))

        item.refresh_from_db()
        assert item.quantity == 1

    def test_deletes_item_at_quantity_one(self, client, user, product):
        item = CartItem.objects.create(product=product, quantity=1, user=user)
        client.force_login(user)

        client.get(reverse('remove_from_cart', args=[product.id, item.id]))

        assert not CartItem.objects.filter(id=item.id).exists()

    def test_anonymous_without_cart_redirects(self, client, product):
        response = client.get(reverse('remove_from_cart', args=[product.id, 1]))

        assert response.status_code == 302
        assert response['Location'] == reverse('cart')

    def test_cannot_remove_another_users_item(self, client, user, product):
        item = CartItem.objects.create(product=product, quantity=2, user=None)
        client.force_login(user)

        client.get(reverse('remove_from_cart', args=[product.id, item.id]))

        item.refresh_from_db()
        assert item.quantity == 2


class TestRemoveCartItem:
    def test_deletes_item_regardless_of_quantity(self, client, product, variations):
        add_to_cart(client, product)
        add_to_cart(client, product)
        item = CartItem.objects.get()

        client.get(reverse('remove_cart_item', args=[product.id, item.id]))

        assert not CartItem.objects.exists()

    def test_missing_item_returns_404(self, client, user, product):
        client.force_login(user)

        response = client.get(reverse('remove_cart_item', args=[product.id, 999]))

        assert response.status_code == 404


class TestCartView:
    def test_anonymous_without_cart_renders_empty(self, client, db):
        response = client.get(reverse('cart'))

        assert response.status_code == 200
        assert list(response.context['cart_items']) == []
        assert response.context['total'] == 0

    def test_totals_for_session_cart(self, client, product, variations):
        add_to_cart(client, product)
        add_to_cart(client, product)

        response = client.get(reverse('cart'))

        assert response.context['quantity'] == 2
        assert response.context['total'] == 80
        assert response.context['tax'] == pytest.approx(19.2)
        assert response.context['grand_total'] == pytest.approx(99.2)


def test_cart_id_creates_session_for_new_visitor():
    request = RequestFactory().get('/')
    request.session = SessionStore()

    cart_id = _cart_id(request)

    assert cart_id
    assert cart_id == request.session.session_key
