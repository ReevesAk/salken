import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from accounts.models import UserProfile

pytestmark = pytest.mark.django_db


@pytest.fixture
def profile(user):
    return UserProfile.objects.create(user=user, city='London')


@pytest.fixture
def logged_in(client, user, profile):
    client.force_login(user)
    return client


@pytest.mark.parametrize(
    'name', ['dashboard', 'my_orders', 'edit_profile', 'change_password']
)
def test_account_pages_require_login(client, db, name):
    response = client.get(reverse(name))

    assert response.status_code == 302
    assert response['Location'].startswith(reverse('login'))


@pytest.mark.parametrize(
    'name', ['dashboard', 'my_orders', 'edit_profile', 'change_password']
)
def test_account_pages_render(logged_in, name):
    assert logged_in.get(reverse(name)).status_code == 200


def test_dashboard_counts_only_completed_orders(logged_in, user):
    response = logged_in.get(reverse('dashboard'))

    assert response.context['orders_count'] == 0
    assert response.context['userprofile'].user == user


def test_edit_profile_updates_user_and_profile(logged_in, user, profile):
    response = logged_in.post(
        reverse('edit_profile'),
        {
            'first_name': 'Augusta',
            'last_name': 'King',
            'phone_no': '5550199',
            'address_line_1': '12 St James Square',
            'address_line_2': '',
            'city': 'London',
            'state': '',
            'country': 'UK',
        },
    )

    assert response['Location'] == reverse('edit_profile')
    user.refresh_from_db()
    profile.refresh_from_db()
    assert (user.first_name, user.phone_no) == ('Augusta', '5550199')
    assert (profile.address_line_1, profile.country) == ('12 St James Square', 'UK')


class TestChangePassword:
    def post(self, client, current, new, confirm=None):
        return client.post(
            reverse('change_password'),
            {
                'current_password': current,
                'new_password': new,
                'confirm_password': new if confirm is None else confirm,
            },
        )

    def test_changes_password(self, logged_in, user, password):
        self.post(logged_in, password, 'new-secret-pass')

        user.refresh_from_db()
        assert user.check_password('new-secret-pass')

    def test_rejects_wrong_current_password(self, logged_in, user, password):
        self.post(logged_in, 'wrong', 'new-secret-pass')

        user.refresh_from_db()
        assert user.check_password(password)

    def test_rejects_mismatched_confirmation(self, logged_in, user, password):
        self.post(logged_in, password, 'new-secret-pass', confirm='different')

        user.refresh_from_db()
        assert user.check_password(password)


@pytest.mark.parametrize('name', ['dashboard', 'edit_profile'])
def test_pages_create_missing_profile(client, user, name):
    # Accounts made with createsuperuser have no UserProfile.
    client.force_login(user)

    assert client.get(reverse(name)).status_code == 200
    assert UserProfile.objects.filter(user=user).exists()


def png_upload(name='avatar.png'):
    buffer = io.BytesIO()
    Image.new('RGB', (4, 4), 'red').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


def profile_form_data(**extra):
    return {
        'first_name': 'Ada',
        'last_name': 'Lovelace',
        'phone_no': '5550100',
        'address_line_1': '',
        'address_line_2': '',
        'city': 'London',
        'state': '',
        'country': 'UK',
        **extra,
    }


def test_edit_profile_accepts_image_upload(logged_in, profile):
    response = logged_in.post(
        reverse('edit_profile'), profile_form_data(profile_picture=png_upload())
    )

    assert response['Location'] == reverse('edit_profile')
    profile.refresh_from_db()
    assert profile.profile_picture.name.startswith('userprofile/avatar')


def test_edit_profile_rejects_non_image_upload(logged_in, profile):
    fake = SimpleUploadedFile('avatar.png', b'not an image', content_type='image/png')

    response = logged_in.post(
        reverse('edit_profile'), profile_form_data(profile_picture=fake)
    )

    assert response.status_code == 200
    assert 'profile_picture' in response.context['profile_form'].errors
    profile.refresh_from_db()
    assert not profile.profile_picture
