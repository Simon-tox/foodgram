from django.contrib import admin


from users.models import Favorite

from .models import TAGS, Ingredient, Recipe, RecipeIngredient


class TagFilter(admin.SimpleListFilter):
    title = 'tags'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        return TAGS

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__icontains=self.value())


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'likes')
    search_fields = ('name', 'author__username', 'description')
    list_filter = (TagFilter, )
    inlines = [
        RecipeIngredientInline,
    ]

    def likes(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    likes.short_description = 'Добавили в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'dimension')
    search_fields = ('title',)
    list_filter = ('title',)
