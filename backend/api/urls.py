"""URLs API."""
from django.urls import include, path
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/set_password/',
        DjoserUserViewSet.as_view({'post': 'set_password'}),
        name='set-password'
    ),
]
