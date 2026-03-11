"""Сериализаторы пользователей."""
import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from recipes.models import Recipe

from .models import User


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки изображения в формате Base64."""

    def to_internal_value(self, data):
        """Декодировать Base64 в файл."""
        if isinstance(data, str) and data.startswith('data:image'):
            header, imgstr = data.split(';base64,')
            ext = header.split('/')[-1]
            filename = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета данные."""

        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на этого пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(user=request.user).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        """Мета данные."""

        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создать пользователя с хешированным паролем."""
        user = User.objects.create_user(**validated_data)
        return user


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для загрузки аватара."""

    avatar = Base64ImageField()

    class Meta:
        """Мета данные."""

        model = User
        fields = ('avatar',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Минимальное представление рецепта — для списка подписок."""

    class Meta:
        """Мета данные."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    """Пользователь с рецептами — для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta(UserSerializer.Meta):
        """Мета данные."""

        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Вернуть рецепты автора с учётом лимита."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(
            recipes, many=True, context={'request': request}
        ).data
