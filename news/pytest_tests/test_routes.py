import pytest

from pytest_django.asserts import assertRedirects
from django.test.client import Client

from http import HTTPStatus

from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def imposter(django_user_model):
    return django_user_model.objects.create(username='Самозванец')


@pytest.fixture
def imposter_client(imposter):
    client = Client()
    client.force_login(imposter)
    return client


@pytest.fixture
def news():
    some_news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return some_news


@pytest.fixture
def comment(news, author):
    some_comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author
    )
    return some_comment


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ('news:home',
                                      'users:login',
                                      'users:signup',
                                      )
                         )
def test_pages_availability_anonymus(client, url_name):
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_availability_anonymus(client, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
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


@pytest.mark.django_db
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