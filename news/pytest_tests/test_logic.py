from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


FORM_DATA = {'text': 'В отдаленных трущебах Кейптауна...'}


def test_anonymous_user_cant_create_note(client, news, news_detail_url, login_url):
    response = client.post(news_detail_url, data=FORM_DATA)
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    client.post(news_detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_auth_user_can_create_note(author_client, news, author, news_detail_url):
    Comment.objects.all().delete()
    response = author_client.post(news_detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{news_detail_url}#comments'
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_detail_url, data=bad_words_data)
    form = response.context['form']
    assert Comment.objects.count() == 0    
    assert 'text' in form.errors
    assert WARNING in form.errors['text']


def test_author_can_delete_comment(author_client, comment, news_delete_url):
    author_client.post(news_delete_url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment, news_edit_url):
    old_text = comment.text
    old_author = comment.author
    old_news = comment.news
    author_client.post(news_edit_url, data=FORM_DATA)
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == FORM_DATA['text']
    assert edited_comment.text != old_text
    assert edited_comment.author == old_author
    assert edited_comment.news == old_news    


def test_imposter_cant_delete_comment(imposter_client, comment, news_delete_url):
    imposter_client.post(news_delete_url, data=FORM_DATA)
    assert Comment.objects.count() == 1


def test_imposter_cant_edit_comment(imposter_client, comment, news_edit_url):
    old_text = comment.text
    old_author = comment.author
    old_news = comment.news
    imposter_client.post(news_edit_url, data=FORM_DATA)
    actual_comment = Comment.objects.get(id=comment.id)
    assert actual_comment.text == old_text
    assert actual_comment.author == old_author
    assert actual_comment.news == old_news