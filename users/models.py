from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe


class Follow(models.Model):
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Подписан')

    class Meta:
        ordering = ['-author']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='None')]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite', )
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='favorite_recipe')

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [models.UniqueConstraint(fields=['recipe', 'user'],
                                               name='unique_together')]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
