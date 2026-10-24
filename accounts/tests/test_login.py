import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from cart.models import Cart, CartItem

pytestmark = pytest.mark.django_db


def login(client, email, password, **extra):
    return client.post(reverse('login'), {'email': email, 'password': password}, **extra)


def messages_of(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


def test_login_page_renders(client):
    assert client.get(reverse('login')).status_code == 200


def test_valid_credentials_log_in_and_redirect_to_dashboard(client, user, password):
    response = login(client, user.email, password)

    assert response.status_code == 302
    assert response['Location'] == reverse('dashboard')
    assert int(client.session['_auth_user_id']) == user.id


def test_wrong_password_is_rejected(client, user):
    response = login(client, user.email, 'wrong-password')

    assert response['Location'] == reverse('login')
    assert '_auth_user_id' not in client.session
    assert 'Invalid login credentials!' in messages_of(response)


def test_malformed_input_is_rejected_without_authenticating(client, user, password):
    response = login(client, 'not-an-email', password)

    assert response['Location'] == reverse('login')
    assert '_auth_user_id' not in client.session


def test_missing_fields_do_not_raise(client, db):
    response = client.post(reverse('login'), {})

    assert response.status_code == 302


def test_redirects_to_next_from_referer(client, user, password):
    response = login(
        client, user.email, password,
        HTTP_REFERER='http://testserver/accounts/login?next=/cart/checkout/',
    )

    assert response['Location'] == '/cart/checkout/'


def test_ignores_offsite_next_url(client, user, password):
    response = login(
        client, user.email, password,
        HTTP_REFERER='http://testserver/accounts/login?next=https://evil.example/',
    )

    assert response['Location'] == reverse('dashboard')


class TestSessionCartMerge:
    def add_to_cart(self, client, product, **variations):
        client.post(reverse('add_to_cart', args=[product.id]), variations)

    def test_regression_login_with_session_cart_does_not_raise(
        self, client, user, password, product
    ):
        # login() used to call an undefined _card_id() here.
        self.add_to_cart(client, product)

        response = login(client, user.email, password)

        assert response.status_code == 302
        assert CartItem.objects.get().user == user

    def test_new_items_move_to_user(self, client, user, password, product, variations):
        self.add_to_cart(client, product, color='red')

        login(client, user.email, password)

        item = CartItem.objects.get()
        assert item.user == user
        assert list(item.variation.all()) == [variations['red']]

    def test_matching_items_combine_quantities(
        self, client, user, password, product, variations
    ):
        existing = CartItem.objects.create(product=product, quantity=2, user=user)
        existing.variation.add(variations['red'])
        self.add_to_cart(client, product, color='red')
        self.add_to_cart(client, product, color='red')

        login(client, user.email, password)

        existing.refresh_from_db()
        assert existing.quantity == 4
        assert CartItem.objects.count() == 1

    def test_different_variations_stay_separate(
        self, client, user, password, product, variations
    ):
        existing = CartItem.objects.create(product=product, quantity=1, user=user)
        existing.variation.add(variations['red'])
        self.add_to_cart(client, product, color='blue')

        login(client, user.email, password)

        assert CartItem.objects.filter(user=user).count() == 2

    def test_login_without_session_cart(self, client, user, password):
        login(client, user.email, password)

        assert not Cart.objects.exists()
        assert not CartItem.objects.exists()
