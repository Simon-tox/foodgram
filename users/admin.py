from django.contrib import admin

from .models import Favorite, Follow

admin.site.register(Follow)
admin.site.register(Favorite)
