# used to "mock" - replace behaviors for the purpose of testing
from unittest.mock import patch

# this will be used to store one of the values in our recipe object
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    ### Users
    def test_create_user_with_email_succesful(self):
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        # list unpacking in Python's for loop
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    ### Recipe model
    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description. ",
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test if creating a tag is successful (and if str representation of our tag is set up correctly)"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test if creating an ingredient is successful"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name="Ingredient1")

        self.assertEqual(str(ingredient), ingredient.name)

    # this uuid is unique identifier - so that every file has a unique name
    # we're patching the uuid functionality. It generates random filename which is awesome, but for
    # the tests - we want a simple name to be able to identify it easily
    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating path to an image in the system"""
        # here we're replacing the result of uuid with our value
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        # creating a filepath to our new image named example.com
        file_path = models.recipe_image_file_path(None, "example.jpg")

        # checking if the image was saved in the path we've predicted and wanted
        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")
