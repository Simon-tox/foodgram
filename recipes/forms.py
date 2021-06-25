from django import forms

from django.shortcuts import get_object_or_404, redirect, render
from pytils.translit import slugify

from .models import Recipe, RecipeIngredient, Ingredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('name', 'tags', 'cooking_time','image', 'description')
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

