""" Views for the recpi APIs """

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""

    # we're going to be mostly using recipe detail endpoint - delete, update etc
    serializer_class = serializers.RecipeDetailSerializer
    # here we're specifying with which model the Viewset is going to work
    queryset = Recipe.objects.all()
    # in order to use(make requests to) any of these viewsets, users need to use those two
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request"""
        # if we're calling the list endpoint (root of the API), it's going to come up as a general endpoint with all the recipes
        if self.action == "list":
            return serializers.RecipeSerializer

        # otherwise it returns a detail endpoint
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


# we're not gonna directly use this viewset, we're gonna inherit from it in our "actual" viewsets
class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    # this mixin allows us "listing functionality"
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """for "attributes of a recipe" - in this context - ingredients and tags"""

    # users can only authenticate by token
    authentication_classes = [TokenAuthentication]
    # only authenticated users can make requests to this API endpoint
    permission_classes = [IsAuthenticated]

    # get_queryset method exists already, but it returns ALL the tags from all users. We want to return the tags for the currently authenticated user, so we're overriding it
    def get_queryset(self):
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-name")


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
