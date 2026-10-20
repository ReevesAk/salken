import shutil
import tempfile

import pytest

from accounts.models import Account
from category.models import Category
from store.models import Product, Variation


@pytest.fixture(autouse=True)
def _media_root(settings):
    media_root = tempfile.mkdtemp()
    settings.MEDIA_ROOT = media_root
    yield
    shutil.rmtree(media_root, ignore_errors=True)


@pytest.fixture
def product(db):
    category = Category.objects.create(category_name='Shirts', slug='shirts')
    return Product.objects.create(
        product_name='Linen Shirt',
        slug='linen-shirt',
        price=40,
        image='photos/products/linen-shirt.jpg',
        stock=10,
        category=category,
    )


@pytest.fixture
def variations(product):
    return {
        'red': Variation.objects.create(
            product=product, variation_category='color', variation_value='red'
        ),
        'blue': Variation.objects.create(
            product=product, variation_category='color', variation_value='blue'
        ),
        'large': Variation.objects.create(
            product=product, variation_category='size', variation_value='large'
        ),
    }


@pytest.fixture
def password():
    return 'analytical-engine-1843'


@pytest.fixture
def user(db, password):
    account = Account.objects.create_user(
        first_name='Ada',
        last_name='Lovelace',
        username='AdaLovelace',
        email='ada@example.com',
        password=password,
    )
    account.phone_no = '5550100'
    account.is_active = True
    account.save()
    return account
