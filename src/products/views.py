from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.utils import timezone
from django.views.generic import DetailView, ListView

from products.forms import VariationInventoryFormSet
from products.mixins import StaffRequiredMixin
from .models import Product, Variation, Category


class VariationListView(StaffRequiredMixin, ListView):
    model = Variation
    queryset = Variation.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView, self).get_context_data(*args, **kwargs)
        # queryset=self.get_queryset(): product.variation을 출력하기 위해 queryset 옵션 사용
        # 없을 경우 모든 variation
        context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
        return context

    def get_queryset(self):
        queryset = None
        product_pk = self.kwargs.get("pk")
        # print(self.kwargs.get('pk'))  # product_id
        if product_pk:
            product = get_object_or_404(Product, pk=product_pk)
            # 특정 제품(예: 아이폰)의 variation(색상: gold, silver, rose gold 등) 필터링
            queryset = Variation.objects.filter(product=product)
        return queryset

    def post(self, request, *args, **kwargs):
        # request.POST(form) + request.FILES(image)
        formset = VariationInventoryFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save(commit=False)
            for form in formset:
                # cleaned_data 조건이 없을 경우,
                # new_item.product에 의해 빈 폼에 대한 객체가 생성된다
                # 또는 아래은 조건을 이용해 처리할 수 있다.
                # new_item = form.save(commit=False)
                #   if new_item.title:
                if form.cleaned_data:
                    new_item = form.save(commit=False)
                    product_pk = self.kwargs.get('pk')
                    product = get_object_or_404(Product, pk=product_pk)
                    new_item.product = product
                    new_item.save()
            messages.success(request, 'your inventory and prices has been updated')
            return redirect("products")
        raise Http404


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        context["now"] = timezone.now()
        context["query"] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        qs = super(ProductListView, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            qs = self.model.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            try:
                qs2 = self.model.objects.filter(price=query)
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs


class ProductDetailView(DetailView):
    model = Product


def product_detail_view_func(request, id):
    # product_instance = get_object_or_404(Product, id=id)
    template = 'products/product_detail.html'
    try:
        product_instance = Product.objects.get(id=id)
    except Product.DoesNotExist:
        raise Http404

    context = {
        "object": product_instance
    }
    return render(request, template, context)


class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()
    template_name = "products/product_list.html"


class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        # print('1:', obj)  # -> Category
        obj = self.get_object()
        # print('2:', obj.product_set)  # -> default related name(product)
        product_set = obj.product_set.all()
        # print('3:', obj.default_category)
        default_products = obj.default_category.all()
        # 중복 제거
        products = (product_set | default_products).distinct()
        context["products"] = products
        return context
