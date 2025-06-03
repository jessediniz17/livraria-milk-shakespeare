from django.contrib import admin
from .models import Livro

class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'preco')

admin.site.register(Livro, LivroAdmin)