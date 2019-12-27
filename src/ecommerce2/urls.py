from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from newsletter.views import home

urlpatterns = [
    # Examples:
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    # path(r'^contact/$', 'newsletter.views.contact', name='contact'),
    # path('about/', 'ecommerce2.views.about', name='about'),
    # path(r'^blog/', include('blog.urls')),
    path('accounts/', include('registration.backends.default.urls')),
    path('products/', include('products.urls')),
    path('categories/', include('products.urls_categories')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
