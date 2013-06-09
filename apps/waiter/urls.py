from django.conf.urls import *

urlpatterns = patterns('waiter.views',
    url(r'^(?P<path>.*)$', 'wait', name='waiter'),
)
