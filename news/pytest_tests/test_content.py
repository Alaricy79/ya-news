import pytest
from django.test.client import Client

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(news_list, home_url):
    client = Client()
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(news_list, home_url):
    client = Client()
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(news, news_detail_url, client, comments):
    response = client.get(news_detail_url).context
    comments_from_response = response['news'].comment_set.all()
    assert comments_from_response.count() == 5
    all_dates = [comment.created for comment in comments_from_response]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


def test_create_note_page_contains_form(news, news_detail_url, client):
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_create_note_page_not_contains_form(news, author_client, news_detail_url):
    response = author_client.get(news_detail_url)
    assert 'form' in response.context


def test_create_note_page_contains_correct_form(news, author_client, news_detail_url):
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)
