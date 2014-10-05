from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'issues/', include('issues.urls', namespace='issues', app_name='issues')),
    url(r'', include('drama.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
            
