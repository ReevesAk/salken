import pytest
from django.contrib.admin.sites import site

from accounts.admin import UserProfileAdmin
from accounts.models import Account, UserProfile

pytestmark = pytest.mark.django_db


@pytest.fixture
def profile_admin():
    return UserProfileAdmin(UserProfile, site)


def test_thumbnail_renders_image_tag(profile_admin, user):
    profile = UserProfile.objects.create(user=user, profile_picture='userprofile/a.png')

    html = profile_admin.thumbnail(profile)

    assert html == (
        '<img src="/media/userprofile/a.png" width="30" style="border-radius:50%;">'
    )


def test_thumbnail_is_empty_without_picture(profile_admin, user):
    profile = UserProfile.objects.create(user=user)

    assert profile_admin.thumbnail(profile) == ''


def test_profile_changelist_renders(client, user):
    admin = Account.objects.create_superuser(
        first_name='Grace', last_name='Hopper', email='grace@example.com',
        username='GraceHopper', password='cobol-1959',
    )
    client.force_login(admin)
    UserProfile.objects.create(user=user, profile_picture='userprofile/a.png')

    response = client.get('/secure-login/accounts/userprofile/')

    assert response.status_code == 200
