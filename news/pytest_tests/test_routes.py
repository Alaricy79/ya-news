from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('url_name', ('news:home',
                                      'users:login',
                                      'users:signup',
                                      )
                         )
def test_pages_availability_anonymus(client, url_name):
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_availability_anonymus(client, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name,client_fixture,expected_status', [
    ('news:delete', 'author_client', HTTPStatus.OK),
    ('news:edit', 'author_client', HTTPStatus.OK),
    ('news:delete', 'imposter_client', HTTPStatus.NOT_FOUND),
    ('news:edit', 'imposter_client', HTTPStatus.NOT_FOUND),
])
def test_pages_availability_and_restriction(request, comment, url_name,
                                            client_fixture, expected_status):
    client = request.getfixturevalue(client_fixture)
    url = reverse(url_name, args=[comment.id])
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    ),
)

def test_redirects(client, name, news_object):
    login_url = reverse('users:login')
    url = reverse(name, args=(news_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)