import pytest

from http import HTTPStatus

from django.urls import reverse

from news.models import News


@pytest.fixture
def news_fixture():
    some_news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return some_news


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', (
    'news:home',
    'users:login',
    'users:signup',
))
def test_pages_availability_anonymus(client, url_name):
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_availability_anonymus(client, news_fixture):
    url = reverse('news:detail', args=[news_fixture.id])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
