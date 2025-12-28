from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    (
        ('home_url', 'client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),

        ('news_detail_url', 'client', HTTPStatus.OK),

        ('news_edit_url', 'author_client', HTTPStatus.OK),
        ('news_delete_url', 'author_client', HTTPStatus.OK),

        ('news_edit_url', 'imposter_client', HTTPStatus.NOT_FOUND),
        ('news_delete_url', 'imposter_client', HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_status_codes(
    request, url_fixture, client_fixture, expected_status
):
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)

    response = client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    (
        'news_edit_url',
        'news_delete_url',
    ),
)
def test_redirects_for_anonymous(client, login_url, request, url_fixture):
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
