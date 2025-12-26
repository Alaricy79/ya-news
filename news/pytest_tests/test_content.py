import pytest
from datetime import datetime, timedelta
from pytest_django.asserts import assertRedirects
from django.test.client import Client

from http import HTTPStatus

from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def news():
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text=f'Просто текст. {index}',
            date=today - timedelta(days=index)
        )
        for index in range(11)
    ]
    return News.objects.bulk_create(news_list)


@pytest.mark.django_db
def test_news_count(news):
    client = Client()
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == 10
