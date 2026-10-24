import pytest
from django.urls import reverse

from accounts.models import Account
from orders.models import Order, OrderProduct

pytestmark = pytest.mark.django_db


def make_order(user, product, number):
    order = Order.objects.create(
        user=user, order_number=number, first_name='Ada', last_name='Lovelace',
        phone='5550100', email=user.email, address_line_1='12 St James Square',
        country='UK', state='London', city='London', order_total=81.6, tax=1.6,
        is_ordered=True,
    )
    OrderProduct.objects.create(
        order=order, user=user, product=product, quantity=2, product_price=40,
        ordered=True,
    )
    return order


@pytest.fixture
def other_user(db):
    return Account.objects.create_user(
        first_name='Grace', last_name='Hopper', username='GraceHopper',
        email='grace@example.com', password='cobol-1959',
    )


def test_order_detail_shows_own_order(client, user, product):
    order = make_order(user, product, '20260101')
    client.force_login(user)

    response = client.get(reverse('order_detail', args=[order.order_number]))

    assert response.status_code == 200
    assert response.context['order'] == order
    assert response.context['subtotal'] == 80


def test_order_detail_hides_other_users_orders(client, user, other_user, product):
    order = make_order(other_user, product, '20260102')
    client.force_login(user)

    response = client.get(reverse('order_detail', args=[order.order_number]))

    assert response.status_code == 404


def test_my_orders_lists_only_own_orders(client, user, other_user, product):
    mine = make_order(user, product, '20260103')
    make_order(other_user, product, '20260104')
    client.force_login(user)

    response = client.get(reverse('my_orders'))

    assert list(response.context['orders']) == [mine]
