from django.urls import path

from products.views import *

urlpatterns = [
    # url(r'^products/', include('products.urls')),
    path('<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('', ProductListView.as_view(), name='products'),
]
