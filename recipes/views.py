import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import View
from pytils.translit import slugify

from users.models import Favorite, Follow, get_user_model

from .forms import RecipeForm
from .mixins import MainMixin
from .models import Ingredient, Recipe, RecipeIngredient


class IndexView(MainMixin, View):
    title = 'Рецепты'
    tab = 'index'


class FavoriteView(LoginRequiredMixin, MainMixin, View):
    login_url = reverse_lazy('login')
    title = 'Избранное'
    tab = 'favorites'

    def get(self, request):
        self.queryset = Recipe.objects.filter(favorite__user=request.user)
        return super().get(request)

    def post(self, request):
        data = json.loads(request.body)
        try:
            recipe_id = data['id']
        except TypeError:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj, created = Favorite.objects.get_or_create(recipe=recipe,
                                                      user=request.user)
        return JsonResponse(data={'success': created}, safe=True)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        get_object_or_404(Favorite, recipe=recipe, user=request.user).delete()
        return JsonResponse(data={'success': True}, safe=True)


class SubscribeView(LoginRequiredMixin, MainMixin, View):
    login_url = reverse_lazy('login')
    title = 'Подписки'
    tab = 'subscriptions'
    card_template = 'author_card.html'
    tags = False

    def get(self, request):
        self.queryset = (get_user_model().
                         objects.filter(following__user=request.user))
        return super().get(request)

    def post(self, request):
        data = json.loads(request.body)
        try:
            recipe_id = data['id']
        except TypeError:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        author = get_object_or_404(get_user_model(), id=recipe_id)
        obj, created = Follow.objects.get_or_create(author=author,
                                                    user=request.user)
        return JsonResponse(data={'success': created}, safe=True)

    def delete(self, request, user_id):
        author = get_object_or_404(get_user_model(), id=user_id)
        get_object_or_404(Follow, author=author, user=request.user).delete()
        return JsonResponse(data={'success': True}, safe=True)


class PurchaseView(MainMixin, View):
    template = 'shop_list.html'
    title = 'Список покупок'
    tab = 'purchases'

    def post(self, request):
        data = json.loads(request.body)
        try:
            recipe_id = data['id']
        except TypeError:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        get_object_or_404(Recipe, id=recipe_id)
        purchases = request.session['purchases']
        success = False
        if recipe_id not in purchases:
            purchases.append(recipe_id)
            request.session['purchases'] = purchases
            success = True
        return JsonResponse(data={'success': success}, safe=True)

    def delete(self, request, recipe_id):
        id_recipe = str(recipe_id)
        get_object_or_404(Recipe, id=recipe_id)
        purchases = request.session['purchases']
        success = False
        if id_recipe in purchases:
            purchases.remove(id_recipe)
            request.session['purchases'] = purchases
            success = True
        return JsonResponse(data={'success': success}, safe=True)


def single_recipe(request, username, slug):
    recipe = get_object_or_404(Recipe, slug=slug, author__username=username)
    return render(request, 'single_page.html', context={'recipe': recipe})


class CreateRecipeView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        form = RecipeForm()
        return render(request, 'recipe_form.html', context={'form': form})

    def post(self, request):
        form = RecipeForm(request.POST, files=request.FILES)
        if form.is_valid():
            ing_names = request.POST.getlist('nameIngredient')
            ing_values = request.POST.getlist('valueIngredient')
            ing_units = request.POST.getlist('unitsIngredient')

            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.slug = slugify(recipe.name)

            if len(ing_names) == len(ing_units) == len(ing_values) != 0:
                for values in ing_values:
                    if int(values) >= 0:
                        recipe.save()
                        counter = len(ing_names)
                        for i in range(counter):
                            ingredient = get_object_or_404(
                                Ingredient,
                                title=ing_names[i],
                                dimension=ing_units[i]
                            )
                            RecipeIngredient.objects.get_or_create(
                                recipe=recipe,
                                ingredient=ingredient,
                                amount=ing_values[i])
                    else:
                        return render(request, 'recipe_form.html',
                              context={
                                  'form': form,
                                  'ing_error': 'Значение должно быть больше или равно 0.'
                              })

            else:
                return render(request, 'recipe_form.html',
                              context={
                                  'form': form,
                                  'ing_error': 'Добавьте ингредиентов'
                              })
        else:
            return render(request, 'recipe_form.html', context={'form': form})

        return redirect('recipe', username=recipe.author, slug=recipe.slug)
class EditRecipeView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, username, slug):
        recipe = get_object_or_404(Recipe,
                                   slug=slug,
                                   author__username=username)
        if recipe.author != request.user:
            return redirect('recipe', username=recipe.author, slug=recipe.slug)

        form = RecipeForm(instance=recipe)
        return render(request, 'recipe_form.html',
                      context={'form': form, 'recipe': recipe})

    def post(self, request, username, slug):
        get_object_or_404(get_user_model(), username=username)
        recipe = get_object_or_404(Recipe, slug=slug)
        if recipe.author != request.user:
            return redirect('recipe', username=recipe.author, slug=recipe.slug)

        form = RecipeForm(request.POST, files=request.FILES, instance=recipe)
        if form.is_valid():
            ing_names = request.POST.getlist('nameIngredient')
            ing_values = request.POST.getlist('valueIngredient')
            ing_units = request.POST.getlist('unitsIngredient')

            if len(ing_names) == len(ing_units) == len(ing_values) != 0:
                for values in ing_values:
                    if int(values) >= 0:
                        form.save()
                        RecipeIngredient.objects.filter(recipe=recipe).delete()
                        counter = len(ing_names)
                        for i in range(counter):
                            ingredient = get_object_or_404(
                                Ingredient,
                                title=ing_names[i],
                                dimension=ing_units[i]
                            )
                            RecipeIngredient.objects.get_or_create(
                                recipe=recipe,
                                ingredient=ingredient,
                                amount=ing_values[i])
                    else:
                        return render(request, 'recipe_form.html',
                                      context={
                                          'form': form,
                                          'ing_error': 'Значение должно быть больше или равно 0.'
                                      })

            else:
                return render(request, 'recipe_form.html',
                              context={
                                  'form': form,
                                  'ing_error': 'Добавьте ингредиентов'
                              })
        else:
            return render(request, 'recipe_form.html',
                          context={'form': form, 'recipe': recipe})
        return redirect('recipe', username=recipe.author, slug=recipe.slug)


@login_required
def delete_recipe(request, username, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    if recipe.author != request.user:
        return redirect('recipe', username=recipe.author, slug=recipe.slug)
    recipe.delete()
    return redirect('index')


# operating requests


def list_ingredients(request):
    try:
        query = request.GET.get('query').lower()
    except TypeError:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    ingredients = Ingredient.objects.filter(title__istartswith=query).values(
        'title', 'dimension'
    )
    return JsonResponse(list(ingredients), safe=False)


def edit_tag(request, tag):
    previous_url = request.META.get('HTTP_REFERER')
    tags = request.session.get('tag_list')
    if tag in tags:
        tags.remove(tag)
    else:
        tags.append(tag)
    request.session['tag_list'] = tags
    return redirect(previous_url)

def download_purchases(request):
    filename = 'purchase_list.txt'
    ids = request.session['purchases']
    all_ingredients = RecipeIngredient.objects.filter(recipe_id__in=ids)
    ingredients = {}
    for ingredient in all_ingredients:
        if ingredient.ingredient.title in ingredients:
            ingredients[ingredient.ingredient.title][0] += ingredient.amount
        else:
            ingredients[ingredient.ingredient.title] = [
                ingredient.amount, ingredient.ingredient.dimension
            ]

    content = ['Shopping list by Foodgram\n\n']
    for i, v in ingredients.items():
        content.append(f'{i.capitalize()} - {v[0]}{v[1]}\n')

    response = HttpResponse(content, content_type='text/plain')
    if not len(ingredients.keys()):
        return redirect('purchases')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename
    )
    return response


def about(request):
    return render(request, 'misc/about.html')


def spec(request):
    return render(request, 'misc/spec.html')


def page_not_found(request, exception):
    return render(request, 'misc/404.html',
                  {'path': request.path}, status=HTTPStatus.NOT_FOUND)


def server_error(request):
    return render(request, 'misc/500.html'
                  , status=HTTPStatus.INTERNAL_SERVER_ERROR)
