""" Views for the recpi APIs """

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma-separated list of IDs to filter",
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="Comma-separated list of ingredient IDs to filter",
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""

    # we're going to be mostly using recipe detail endpoint - delete, update etc
    serializer_class = serializers.RecipeDetailSerializer
    # here we're specifying with which model the Viewset is going to work
    queryset = Recipe.objects.all()
    # in order to use(make requests to) any of these viewsets, users need to use those two
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers"""
        # "1, 2, 3" => [1, 2, 3]
        return [int(str_id) for str_id in qs.split(".")]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        # if there are any tags/ingredients
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        # if we're calling the list endpoint (root of the API), it's going to come up as a general endpoint with all the recipes
        if self.action == "list":
            return serializers.RecipeSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer

        # otherwise it returns a detail endpoint
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    # creating a custom action. "detail=True" signifies that we're working with the "detail" endpoint, not the list of all recipes
    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            # save the image to the db
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # if we get here, we assume the serializer was not valid - thus showing the error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# we're not gonna directly use this viewset, we're gonna inherit from it in our "actual" viewsets - tags and ingredients
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
