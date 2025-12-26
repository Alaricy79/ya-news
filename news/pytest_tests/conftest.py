from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from django.test.client import Client
from django.utils import timezone

from django.conf import settings
from news.models import News, Comment


# ───── users ─────

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


# ───── objects ─────

@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        text='Комментарий',
        author=author,
    )


@pytest.fixture
def news_list():
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text=f'Просто текст. {index}',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def comments(author, news):
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'some text in comment N{index}'
        )
        for index in range(5)
    ]
    Comment.objects.bulk_create(comments)
    for index, comment in enumerate(Comment.objects.all().order_by('id')[:5]):
        comment.created = now + timedelta(days=index)
        comment.save(update_fields=['created'])

# ───── urls ─────

@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def news_edit_url(comment):
    return reverse('news:edit', args=[comment.id])


@pytest.fixture
def news_delete_url(comment):
    return reverse('news:delete', args=[comment.id])