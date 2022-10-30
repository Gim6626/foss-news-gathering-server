import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from gatherer.models import *
from django.forms.models import model_to_dict
import random
import string
from django.utils.http import urlencode
from rest_framework.test import APIRequestFactory


TEST_USERNAME = 'admin'
TEST_PASSWORD = 'adminadmin'


class TestMixin:

    def login(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def strip_id(self, dictionary):
        return self.strip_fields(dictionary, ['id'])

    def strip_fields(self, dictionary, bad_keys):
        dictionary = {k: v for k, v in dictionary.items() if k not in bad_keys}
        return dictionary

    def add_params_to_url(self, url, params):
        if params:
            return f'{url}?{urlencode(params)}'
        else:
            return url


def with_login(func):
    def _wrapper(*args, **kwargs):
        args[0].login()
        func(*args, **kwargs)
    return _wrapper


class RandomEntityGenerator:

    @classmethod
    def generate(cls):
        return {}

    # Make return word instead of random mess of characters
    @classmethod
    def random_word(cls, length=5):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


class RandomKeywordGenerator(RandomEntityGenerator):

    # TODO: Make it really random
    @classmethod
    def generate(cls):
        return {
            'name': 'Linux',
            'content_category': DigestRecordContentCategory.KnD.name,
            'is_generic': False,
            'proprietary': False,
            'enabled': True,
        }


class RandomProjectGenerator(RandomEntityGenerator):

    @classmethod
    def generate(cls):
        return {
            'name': cls.random_word(),
        }


class RandomDigestRecordGenerator(RandomEntityGenerator):

    @classmethod
    def generate(cls, **kwargs):
        return {
            'dt': datetime.datetime.now().isoformat(),
            'source': None,
            'gather_dt': datetime.datetime.now().isoformat(),
            'title': cls.random_word(),
            'url': cls.random_word(),
            'additional_url': None,
            'state': DigestRecordState.UNKNOWN.name,
            'digest_issue': None,
            'is_main': None,
            'content_type': None,
            'content_category': None,
            'keywords': None,
            'title_keywords': [],
            'projects': None if not kwargs['projects'] else kwargs['projects'],
            'language': None,
            'description': None,
            'cleared_description': None,
            'text': None,
        }


class KeywordViewSetTests(APITestCase, TestMixin):

    def test_without_login(self):
        url = reverse('keyword-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @with_login
    def test_create_keyword(self):
        url = reverse('keyword-list')
        example_keyword = RandomKeywordGenerator.generate()
        response = self.client.post(url, example_keyword)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Keyword.objects.count(), 1)
        created_object_without_id = self.strip_id(model_to_dict(Keyword.objects.get()))
        self.assertEqual(created_object_without_id, example_keyword)

    @with_login
    def test_read_one_keyword(self):
        url = reverse('keyword-list')
        example_keyword = RandomKeywordGenerator.generate()
        response = self.client.post(url, example_keyword)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-detail', kwargs={'pk': Keyword.objects.last().pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.strip_id(response.json()), example_keyword)

    @with_login
    def test_read_multiple_keywords(self):
        url = reverse('keyword-list')
        example_keyword = RandomKeywordGenerator.generate()
        response = self.client.post(url, example_keyword)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(self.strip_id(response.json()['results'][0]), example_keyword)

    @with_login
    def test_update_keyword(self):
        url = reverse('keyword-list')
        example_keyword = RandomKeywordGenerator.generate()
        response = self.client.post(url, example_keyword)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-detail', kwargs={'pk': Keyword.objects.last().pk})
        new_name = 'BSD'
        response = self.client.patch(url, {'name': new_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        changed_object_without_id = self.strip_id(model_to_dict(Keyword.objects.get()))
        original_object_with_changed_name = example_keyword.copy()
        original_object_with_changed_name['name'] = new_name
        self.assertEqual(changed_object_without_id, original_object_with_changed_name)

    @with_login
    def test_delete_keyword(self):
        url = reverse('keyword-list')
        example_keyword = RandomKeywordGenerator.generate()
        response = self.client.post(url, example_keyword)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('keyword-detail', kwargs={'pk': Keyword.objects.last().pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Keyword.objects.count(), 0)


class OldestNotCategorizedDigestRecordViewSetTests(APITestCase, TestMixin):

    def test_without_login(self):
        url = reverse('digest-record/not-categorized/oldest-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @with_login
    def test_get(self):
        # Create project
        url = reverse('project-list')
        example_project = RandomProjectGenerator.generate()
        self.client.post(url, example_project)
        project_id = Project.objects.get().pk
        project_name = Project.objects.get().name
        # Create 2 digest records
        url = reverse('digest-record-list')
        from_bot = False
        example_digest_record_1 = RandomDigestRecordGenerator.generate(projects=[project_id], from_bot=from_bot)
        example_digest_record_2 = RandomDigestRecordGenerator.generate(projects=[project_id], from_bot=from_bot)
        self.client.post(url, example_digest_record_1, format='json')
        self.client.post(url, example_digest_record_2, format='json')
        # Get oldest not categorized digest record
        url = self.add_params_to_url(reverse('digest-record/not-categorized/oldest-list'), {'project': project_name, 'from-bot': from_bot})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['results'][0]['title'],
                         example_digest_record_1['title'])
