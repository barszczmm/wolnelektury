
from django.conf.urls import *

urlpatterns = patterns('oai.views',
                       url(r'^$', 'oaipmh', name='oaipmh'))
