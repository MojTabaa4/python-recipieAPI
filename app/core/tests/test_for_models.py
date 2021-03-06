from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from core import models


def dummy_user(email='test@gmail.com', password='12345'):
    """a  dummy user for test"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_user_created(self):
        '''check the created user has required email conditions'''
        email = 'mathew@gmail.com'
        password = 'daredevil123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_super_user_created(self):
        '''check created user is staff with superuser permissions'''
        email = 'ashok@example.com'
        password = '123Ashok'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_tag_str(self):
        """Test the tag string """
        tag = models.Tag.objects.create(
            user=dummy_user(),
            name='Curry'
            )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string generated for print """
        ingredients = models.Ingredient.objects.create(
            user=dummy_user(),
            name='masala'
        )

        self.assertEqual(str(ingredients), ingredients.name)

    def test_recipe_str(self):
        """Test recipe string generated"""
        recipe = models.Recipe.objects.create(
            user=dummy_user(),
            title='indian beef curry',
            time_minutes=45,
            price=100.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_path(None, 'image.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)        

        
            