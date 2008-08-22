# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('catalogue.views',
    url(r'^$', 'main_page', name='main_page'),
    url(r'^lektury/', 'book_list'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/zestawy/', 'book_sets'),
    url(r'^zestawy/nowy/$', 'new_set'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/$', 'book_detail'),
    url(r'^tags/$', 'tags_starting_with', name='hint'),
    url(r'^(?P<tags>[a-zA-Z-/]+)/$', 'tagged_book_list', name='tagged_book_list'),
)

