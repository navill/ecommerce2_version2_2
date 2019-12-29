from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from newsletter.views import home
from carts.views import CartView, ItemCountView, CheckoutView
# from orders.views import AddressSelectFormView
from orders.views import AddressSelectFormView

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
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/count/', ItemCountView.as_view(), name='item_count'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/address/', AddressSelectFormView.as_view(), name='order_address'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
