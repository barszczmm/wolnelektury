# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django import forms

from newtagging.admin import TaggableModelAdmin, TaggableModelForm
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

    prepopulated_fields = {'slug': ('title',), 'common_slug': ('title',),}

    inlines = [MediaInline]

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('cover', 'extra_info', 'parent_number',
                        'html_file', 'epub_file', 'mobi_file', 'txt_file', 'fb2_file')
        return super(BookAdmin, self).add_view(request, form_url=form_url,
                                               extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        if not request.GET.has_key('advanced'):
            self.form = forms.ModelForm
            self.fields = ('title', 'description', 'gazeta_link', 'wiki_link')
            self.readonly_fields = ('title',)
            self.prepopulated_fields = {}
        else:
            self.form = TaggableModelForm
            self.fields = ()
            self.exclude = ('cover', 'extra_info', 'parent_number',
                            'html_file', 'epub_file', 'mobi_file', 'txt_file', 'fb2_file')

        return super(BookAdmin, self).change_view(request, object_id,
                                                  extra_context=extra_context)


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
