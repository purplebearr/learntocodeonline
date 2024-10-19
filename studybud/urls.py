from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from base.sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'static': StaticViewSitemap
}

urlpatterns = [
    path('django-admin/', admin.site.urls),
    #path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),

    path('wagtail-admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('community/', include(wagtail_urls)),

    path('', include('base.urls')),
    path('api/', include('base.api.urls')),
    path("accounts/", include("allauth.urls")),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += path("__debug__/", include("debug_toolbar.urls")),




#path("", include("googleauthentication.urls"))
