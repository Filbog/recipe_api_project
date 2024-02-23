""" URL mappings for the recipe app"""

from django.urls import (
    path,
    include,
)

# used to automatically create routes for all the different options available for a view
from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()
# creating a new endpoint - /recipes
router.register("recipes", views.RecipeViewSet)
router.register("tags", views.TagViewSet)
router.register("ingredients", views.IngredientViewSet)

app_name = "recipe"

urlpatterns = [path("", include(router.urls))]
