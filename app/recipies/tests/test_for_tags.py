from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipies.serializer import TagSerializer


TAGS_URL = reverse('recipies:tag-list')


class PublicTagsApiTests(TestCase):
    """Test for publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'ashok@gmail.com',
            'openit'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='pommes') #creates dummy tags
        Tag.objects.create(user=self.user, name='wurst')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)#creates serializer for all tag objectts
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_for_particular_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'thanos@princesslea.com',
            'snap'
        )
        Tag.objects.create(user=user2, name='bloodymary')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)


    def test_fetching_tag_assigned_to_recipes(self):
        """Test filtering tags """

        tag1 = Tag.objects.create(user=self.user, name='italian')
        tag2 = Tag.objects.create(user=self.user, name='chineese')
        recipe = Recipe.objects.create(
            title='sphaghetti',
            time_minutes=12,
            price=1.00,
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


    def test_fetching_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='german')
        recipe1 = Recipe.objects.create(
            title='brattwurst',
            time_minutes=5,
            price=3.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        
        recipe2 = Recipe.objects.create(
            title='beef curry',
            time_minutes=3,
            price=2.00,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)