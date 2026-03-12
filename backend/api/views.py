"""Импорты."""
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscription, User

from .filters import RecipeFilter
from .serializers import (AvatarSerializer, IngredientSerializer,
                          RecipeMinifiedSerializer, RecipeSerializer,
                          TagSerializer, UserCreateSerializer,
                          UserSerializer, UserWithRecipesSerializer)


def short_link_redirect(request, short_link):
    """Редирект с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect(f'/recipes/{recipe.id}/')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Пользователи: список и детальная информация."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        """Регистрация нового пользователя."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Получить информацию о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        """Загрузить или удалить аватар текущего пользователя."""
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )

        if not user.avatar:
            return Response(
                {'detail': 'Аватар отсутствует.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан текущий пользователь."""
        authors = User.objects.filter(followers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(
            page if page is not None else authors,
            many=True,
            context={'request': request}
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписаться / отписаться от пользователя."""
        author = self.get_object()
        user = request.user

        if user == author:
            return Response(
                {'error': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            _, created = Subscription.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserWithRecipesSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(
            user=user, author=author
        ).delete()
        if not deleted:
            return Response(
                {'error': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги — только чтение."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты — только чтение, поиск по началу названия."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты — полный CRUD + избранное + корзина + скачать список покупок."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Автоматически назначить автора при создании рецепта."""
        serializer.save(author=self.request.user)

    def _add_or_remove(self, model, request, pk):
        """Добавить/удалить из избранного или корзины."""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                return Response(
                    {'detail': 'Уже добавлено.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                RecipeMinifiedSerializer(
                    recipe, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        deleted, _ = model.objects.filter(user=user, recipe=recipe).delete()
        if not deleted:
            return Response(
                {'detail': 'Не найдено.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавить/убрать рецепт из избранного."""
        return self._add_or_remove(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавить/убрать рецепт из корзины покупок."""
        return self._add_or_remove(ShoppingCart, request, pk)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[IsAuthenticatedOrReadOnly]
    )
    def get_link(self, request, pk=None):
        """Получить короткую ссылку на рецепт."""
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f'/s/{recipe.short_link}/')
        return Response({'short-link': short_url})

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок текущего пользователя в TXT."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        if not ingredients.exists():
            return Response(
                {'detail': 'Список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lines = ['Список покупок:\n']
        for item in ingredients:
            lines.append(
                f"- {item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total_amount']}\n"
            )

        response = HttpResponse(
            ''.join(lines),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
