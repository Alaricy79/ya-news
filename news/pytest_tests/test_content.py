from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news_list():
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
def test_news_count(news_list):
    client = Client()
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == 10


@pytest.mark.django_db
def test_news_order(news_list):
    client = Client()
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.fixture
def news():
    return News.objects.create(
        title='Новость c коментариями',
        text='Просто текст новости с коментами',
    )


@pytest.fixture
def comments(author, news):
    now = datetime.now()
    comments = []
    for index in range(5):
        comments.append(Comment(
            news=news,
            author=author,
            text=f'some text in comment N{index}',
            created=now + timedelta(days=index)
        ))
    Comment.objects.bulk_create(comments)
    return Comment.objects


@pytest.mark.django_db
def test_comments_order(news):
    client = Client()
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url).context
    comments = response['news'].comment_set.all()
    all_dates = [comment.created for comment in comments]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_create_note_page_contains_form(news):
    client = Client()
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_create_note_page_not_contains_form(news, author_client):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context