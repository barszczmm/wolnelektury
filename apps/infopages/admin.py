from django.contrib import admin

from modeltranslation.admin import TranslationAdmin
from infopages.models import InfoPage


class InfoPageAdmin(TranslationAdmin):
    list_display = ('title', 'slug', 'main_page')
    exclude = ('right_column_pl',)

admin.site.register(InfoPage, InfoPageAdmin)