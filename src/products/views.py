from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
# Create your views here.
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Product


class ProductListView(ListView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        context["now"] = timezone.now()
        return context


class ProductDetailView(DetailView):
    model = Product


def product_detail_view_func(request, id):
    product_instance = get_object_or_404(Product, id=id)
    template = 'products/product_detail.html'
    try:
        product_instance = Product.objects.get(id=id)
    except Product.DoesNotExist:
        raise Http404

    context = {
        "object": product_instance
    }
    return render(request, template, context)
