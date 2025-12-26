import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse
from django.test.client import Client
from news.forms import BAD_WORDS, WARNING
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
def client():
    return Client()


@pytest.fixture
def news():
    return News.objects.create(
        title='Однажды',
        text='Я просто устану писать эти программы',
    )


@pytest.fixture
def form_data():
    return {
        'text': 'В отдаленных трущебах Кейптауна...',
    }


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_auth_user_can_create_note(author_client, news, form_data, author):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == 302
    assert response.url == f'{url}#comments'
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0
