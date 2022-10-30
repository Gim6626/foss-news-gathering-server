from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from gatherer.models import *
from django.forms.models import model_to_dict


TEST_USERNAME = 'admin'
TEST_PASSWORD = 'adminadmin'


class TestMixin:

    def login(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def strip_id(self, dictionary):
        dictionary = {k: v for k, v in dictionary.items() if k != 'id'}
        return dictionary


def with_login(func):
    def _wrapper(*args, **kwargs):
        args[0].login()
        func(*args, **kwargs)
    return _wrapper


class KeywordViewSetTests(APITestCase, TestMixin):

    EXAMPLE_KEYWORD = {
        'name': 'Linux',
        'content_category': DigestRecordContentCategory.KnD.name,
        'is_generic': False,
        'proprietary': False,
        'enabled': True,
    }

    def test_without_login(self):
        url = reverse('keyword-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @with_login
    def test_create_keyword(self):
        url = reverse('keyword-list')
        response = self.client.post(url, self.EXAMPLE_KEYWORD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Keyword.objects.count(), 1)
        created_object_without_id = self.strip_id(model_to_dict(Keyword.objects.get()))
        self.assertEqual(created_object_without_id, self.EXAMPLE_KEYWORD)

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
        changed_object_without_id = self.strip_id(model_to_dict(Keyword.objects.get()))
        original_object_with_changed_name = self.EXAMPLE_KEYWORD.copy()
        original_object_with_changed_name['name'] = new_name
        self.assertEqual(changed_object_without_id, original_object_with_changed_name)

    @with_login
    def test_delete_keyword(self):
        url = reverse('keyword-list')
        response = self.client.post(url, self.EXAMPLE_KEYWORD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-detail', kwargs={'pk': Keyword.objects.last().pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Keyword.objects.count(), 0)
