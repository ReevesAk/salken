import json

import pytest
from django.core import mail
from django.urls import reverse

from cart.models import CartItem
from orders.models import Order, OrderProduct, Payment

pytestmark = pytest.mark.django_db

BILLING = {
    'first_name': 'Ada',
    'last_name': 'Lovelace',
    'phone': '5550100',
    'email': 'ada@example.com',
    'address_line_1': '12 St James Square',
    'address_line_2': '',
    'country': 'UK',
    'state': 'London',
    'city': 'London',
    'order_note': '',
}


@pytest.fixture
def logged_in(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def cart_item(user, product, variations):
    item = CartItem.objects.create(product=product, quantity=2, user=user)
    item.variation.add(variations['red'])
    return item


def place_order(client, data=BILLING):
    return client.post(reverse('place_order'), data)


def pay(client, order, trans_id='TX-1'):
    return client.post(
        reverse('payments'),
        json.dumps({
            'orderID': order.order_number,
            'transID': trans_id,
            'payment_method': 'PayPal',
            'status': 'COMPLETED',
        }),
        content_type='application/json',
    )


class TestCheckout:
    def test_requires_login(self, client, db):
        response = client.get(reverse('checkout'))

        assert response['Location'].startswith(reverse('login'))

    def test_shows_cart_totals(self, logged_in, cart_item):
        response = logged_in.get(reverse('checkout'))

        assert response.status_code == 200
        assert response.context['total'] == 80
        assert response.context['grand_total'] == pytest.approx(81.6)


class TestPlaceOrder:
    def test_requires_login(self, client, db):
        response = place_order(client)

        assert response['Location'].startswith(reverse('login'))

    def test_empty_cart_redirects_to_store(self, logged_in):
        response = place_order(logged_in)

        assert response['Location'] == reverse('store')
        assert not Order.objects.exists()

    def test_creates_pending_order_with_totals(self, logged_in, user, cart_item):
        response = place_order(logged_in)

        assert response.status_code == 200
        order = Order.objects.get()
        assert order.user == user
        assert order.is_ordered is False
        assert order.order_total == pytest.approx(81.6)
        assert order.tax == pytest.approx(1.6)
        assert order.order_number.endswith(str(order.id))
        assert response.context['order'] == order

    def test_invalid_billing_redirects_to_checkout(self, logged_in, cart_item):
        response = place_order(logged_in, {**BILLING, 'email': 'not-an-email'})

        assert response['Location'] == reverse('checkout')
        assert not Order.objects.exists()

    def test_get_redirects_to_checkout(self, logged_in, cart_item):
        assert logged_in.get(reverse('place_order'))['Location'] == reverse('checkout')


class TestPayments:
    def test_completes_order_and_moves_cart(
        self, logged_in, user, product, variations, cart_item
    ):
        place_order(logged_in)
        order = Order.objects.get()

        response = pay(logged_in, order)

        assert response.json() == {'order_number': order.order_number, 'transID': 'TX-1'}
        order.refresh_from_db()
        assert order.is_ordered is True
        assert order.payment.payment_id == 'TX-1'

        ordered = OrderProduct.objects.get()
        assert (ordered.product, ordered.quantity, ordered.product_price) == (product, 2, 40)
        assert list(ordered.variations.all()) == [variations['red']]

        product.refresh_from_db()
        assert product.stock == 8
        assert not CartItem.objects.exists()
        assert mail.outbox[0].to == [user.email]

    def test_unknown_order_returns_404(self, logged_in, cart_item):
        response = pay(logged_in, Order(order_number='missing'))

        assert response.status_code == 404
        assert not Payment.objects.exists()

    def test_requires_post(self, logged_in):
        assert logged_in.get(reverse('payments')).status_code == 405


class TestOrderComplete:
    def test_shows_paid_order(self, logged_in, cart_item):
        place_order(logged_in)
        order = Order.objects.get()
        pay(logged_in, order)

        response = logged_in.get(
            reverse('order_complete'),
            {'order_number': order.order_number, 'payment_id': 'TX-1'},
        )

        assert response.status_code == 200
        assert response.context['subtotal'] == 80

    def test_unknown_order_redirects_home(self, client, db):
        response = client.get(reverse('order_complete'), {'order_number': 'x'})

        assert response['Location'] == reverse('home')
