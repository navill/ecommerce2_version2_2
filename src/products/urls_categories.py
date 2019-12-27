from django.urls import path

from products.views import *

urlpatterns = [
    path('', CategoryListView.as_view(), name='categories'),
    path('<slug>', CategoryDetailView.as_view(), name='category_detail'),
]
