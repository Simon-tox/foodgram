import os

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from multiselectfield import MultiSelectField

TAGS = (
    ('breakfast', 'Завтрак'),
    ('lunch', 'Обед'),
    ('dinner', 'Ужин')
)


class Ingredient(models.Model):
    title = models.CharField(max_length=75, verbose_name='Название')
    dimension = models.CharField(max_length=25, verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} / {self.dimension}'


class Recipe(models.Model):
    name = models.CharField(max_length=75,
                            verbose_name='Название')
    description = models.TextField(max_length=200,
                                   blank=True,
                                   null=True,
                                   verbose_name='Описание')
    slug = models.SlugField(blank=True, null=True)
    tags = MultiSelectField(choices=TAGS, blank=True, null=True)
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    cooking_time = models.PositiveIntegerField(validators=[
        MinValueValidator(1)
    ],
        verbose_name='Время '
                     'приготовления ')
    image = models.ImageField(upload_to='media/recipes/',
                              blank=True, null=True, verbose_name='Фотография')
    pub_date = models.DateTimeField(auto_now=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.name} - {self.author}'

    @property
    def get_image_name(self):
        try:
            return os.path.basename(self.image.url)
        except TypeError:
            return None


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Ингредиент к рецептам'
        verbose_name_plural = 'Ингредиенты к рецептам'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='recipe_ingredient'
        )]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.title}' \
               f' - {self.ingredient.dimension}'

