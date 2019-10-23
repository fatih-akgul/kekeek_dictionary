from django.contrib import admin

from dictionary.models import Dictionary, Word

admin.site.register(Dictionary)
admin.site.register(Word)
