# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from newtagging.admin import TaggableModelAdmin
from catalogue.models import Tag, Book, Fragment, BookMedia, Collection


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_key', 'category', 'has_description',)
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('name',)

    prepopulated_fields = {'slug': ('name',), 'sort_key': ('name',),}
    radio_fields = {'category': admin.HORIZONTAL}


class MediaInline(admin.TabularInline):
    model = BookMedia
    readonly_fields = ['source_sha1']
    extra = 0


class BookAdmin(TaggableModelAdmin):
    tag_model = Tag

    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title',)
    ordering = ('title',)

    prepopulated_fields = {'slug': ('title',)}

    inlines = [MediaInline]


class FragmentAdmin(TaggableModelAdmin):
    tag_model = Tag

    list_display = ('book', 'anchor',)
    ordering = ('book', 'anchor',)


class CollectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Tag, TagAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Fragment, FragmentAdmin)
admin.site.register(Collection, CollectionAdmin)
