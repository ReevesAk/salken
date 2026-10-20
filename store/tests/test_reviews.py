import pytest
from django.urls import reverse

from store.models import ReviewRating

pytestmark = pytest.mark.django_db

REVIEW = {'subject': 'Great fit', 'review': 'Soft and light.', 'rating': 4.5}


def submit(client, product, data=REVIEW, **extra):
    return client.post(reverse('submit_review', args=[product.id]), data, **extra)


def test_requires_login(client, product):
    response = submit(client, product)

    assert response.status_code == 302
    assert response['Location'].startswith(reverse('login'))
    assert not ReviewRating.objects.exists()


def test_creates_review_and_redirects_back(client, user, product):
    client.force_login(user)

    response = submit(client, product, HTTP_REFERER='http://testserver/back/')

    assert response['Location'] == 'http://testserver/back/'
    review = ReviewRating.objects.get()
    assert (review.user, review.product, review.rating) == (user, product, 4.5)
    assert review.ip == '127.0.0.1'


def test_updates_existing_review(client, user, product):
    client.force_login(user)
    submit(client, product)

    submit(client, product, {**REVIEW, 'rating': 2})

    review = ReviewRating.objects.get()
    assert review.rating == 2


def test_redirects_to_product_without_referer(client, user, product):
    client.force_login(user)

    response = submit(client, product)

    assert response['Location'] == product.get_url()


def test_invalid_review_is_not_saved(client, user, product):
    client.force_login(user)

    submit(client, product, {'subject': 'No rating'})

    assert not ReviewRating.objects.exists()


def test_unknown_product_returns_404(client, user, db):
    client.force_login(user)

    response = client.post(reverse('submit_review', args=[999]), REVIEW)

    assert response.status_code == 404
