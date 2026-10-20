import pytest
from django.urls import reverse

from cart.models import CartItem
from category.models import Category
from store.models import Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def hidden_product(product):
    return Product.objects.create(
        product_name='Retired Shirt',
        slug='retired-shirt',
        description='linen',
        price=10,
        image='photos/products/retired.jpg',
        stock=0,
        is_available=False,
        category=product.category,
    )


class TestStore:
    def test_lists_available_products(self, client, product, hidden_product):
        response = client.get(reverse('store'))

        assert response.status_code == 200
        assert list(response.context['products']) == [product]
        assert response.context['product_count'] == 1

    def test_filters_by_category(self, client, product):
        other = Category.objects.create(category_name='Hats', slug='hats')

        response = client.get(reverse('products_by_category', args=[other.slug]))

        assert response.status_code == 200
        assert list(response.context['products']) == []

    def test_unknown_category_returns_404(self, client, db):
        response = client.get(reverse('products_by_category', args=['nope']))

        assert response.status_code == 404


class TestProductDetail:
    def url(self, product):
        return reverse('product_detail', args=[product.category.slug, product.slug])

    def test_renders_product(self, client, product):
        response = client.get(self.url(product))

        assert response.status_code == 200
        assert response.context['single_product'] == product
        assert response.context['incart'] is False
        assert response.context['orderproduct'] is False

    def test_reports_item_in_session_cart(self, client, product):
        client.post(reverse('add_to_cart', args=[product.id]))

        response = client.get(self.url(product))

        assert response.context['incart'] is True

    def test_reports_item_in_user_cart(self, client, user, product):
        CartItem.objects.create(product=product, quantity=1, user=user)
        client.force_login(user)

        response = client.get(self.url(product))

        assert response.context['incart'] is True

    def test_unknown_product_returns_404(self, client, product):
        response = client.get(
            reverse('product_detail', args=[product.category.slug, 'missing'])
        )

        assert response.status_code == 404


class TestSearch:
    def test_matches_name_and_description(self, client, product, hidden_product):
        product.description = 'Breathable summer fabric'
        product.save()

        by_name = client.get(reverse('search'), {'keyword': 'linen'})
        by_description = client.get(reverse('search'), {'keyword': 'summer'})

        assert list(by_name.context['products']) == [product]
        assert list(by_description.context['products']) == [product]
        assert by_name.context['product_count'] == 1

    @pytest.mark.parametrize('params', [{}, {'keyword': ''}, {'keyword': '   '}])
    def test_empty_keyword_returns_no_products(self, client, product, params):
        response = client.get(reverse('search'), params)

        assert response.status_code == 200
        assert response.context['product_count'] == 0
