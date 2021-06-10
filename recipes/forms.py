from django import forms

from django.shortcuts import get_object_or_404, redirect, render
from pytils.translit import slugify

from .models import Recipe, RecipeIngredient, Ingredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('name', 'tags', 'cooking_time', 'image', 'description')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form__input', 'id': 'id_name'}
            ),
            'tags': forms.CheckboxSelectMultiple(),
            'cooking_time': forms.NumberInput(
                attrs={'class': 'form__input', 'id': 'id_time'}),
            'description': forms.Textarea(
                attrs={'class': 'form__textarea',
                       'id': 'id_description',
                       'rows': '8'})
        }

    def checked_tags(self):
        return [value for value, label in self.fields['tags'].choices
                if value in self['tags'].value()]

    def form_safe(self, request):
        form = RecipeForm(request.POST, files=request.FILES)
        if form.is_valid():
            ing_names = request.POST.getlist('nameIngredient')
            ing_values = request.POST.getlist('valueIngredient')
            ing_units = request.POST.getlist('unitsIngredient')

            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.slug = slugify(recipe.name)

            if len(ing_names) == len(ing_units) == len(ing_values) != 0:
                recipe.save()
                for names, units, values in zip(ing_names,
                                                ing_units,
                                                ing_values):
                    ingredient = get_object_or_404(
                        Ingredient,
                        title=names,
                        dimension=units
                    )
                    RecipeIngredient.objects.get_or_create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=values)
            else:
                return render(request, 'recipe_form.html',
                              context={
                                  'form': form,
                                  'ing_error': 'Добавьте ингредиентов'
                              })
        else:
            return render(request, 'recipe_form.html', context={'form': form})

        return redirect('recipe', username=recipe.author, slug=recipe.slug)
