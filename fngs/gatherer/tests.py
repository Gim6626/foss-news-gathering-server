from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from gatherer.models import *


TEST_USERNAME = 'admin'
TEST_PASSWORD = 'adminadmin'


class TestMixin:

    def login(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)


def with_login(func):
    def _wrapper(*args, **kwargs):
        args[0].login()
        func(*args, **kwargs)
    return _wrapper


class KeywordTests(APITestCase, TestMixin):

    EXAMPLE_KEYWORD = {
        'name': 'Linux',
        'content_category': DigestRecordContentCategory.KnD.name,
        'is_generic': False,
        'proprietary': False,
        'enabled': True,
    }

    @with_login
    def test_create_keyword(self):
        url = reverse('keyword-list')
        response = self.client.post(url, self.EXAMPLE_KEYWORD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Keyword.objects.count(), 1)
        self.assertEqual(Keyword.objects.get().name, self.EXAMPLE_KEYWORD['name'])

    @with_login
    def test_read_one_keyword(self):
        url = reverse('keyword-list')
        response = self.client.post(url, self.EXAMPLE_KEYWORD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-detail', kwargs={'pk': Keyword.objects.last().pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], self.EXAMPLE_KEYWORD['name'])

    @with_login
    def test_read_multiple_keywords(self):
        url = reverse('keyword-list')
        response = self.client.post(url, self.EXAMPLE_KEYWORD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['name'], self.EXAMPLE_KEYWORD['name'])

    @with_login
    def test_update_keyword(self):
        url = reverse('keyword-list')
        response = self.client.post(url, self.EXAMPLE_KEYWORD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-detail', kwargs={'pk': Keyword.objects.last().pk})
        new_name = 'BSD'
        response = self.client.patch(url, {'name': new_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Keyword.objects.get().name, new_name)

    @with_login
    def test_delete_keyword(self):
        url = reverse('keyword-list')
        response = self.client.post(url, self.EXAMPLE_KEYWORD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-detail', kwargs={'pk': Keyword.objects.last().pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Keyword.objects.count(), 0)
