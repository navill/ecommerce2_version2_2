from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
# Create your views here.
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin

from carts.models import CartItem, Cart
from orders.forms import GuestCheckoutForm
# from orders.models import UserCheckout, UserAddress, Order
from orders.mixin import CartOrderMixin
from orders.models import UserCheckout, Order
from products.models import Variation


class ItemCountView(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get("cart_id")
            if cart_id == None:
                count = 0
            else:
                cart = Cart.objects.get(id=cart_id)
                count = cart.items.count()
            request.session["cart_item_count"] = count
            return JsonResponse({"count": count})
        else:
            raise Http404


class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = "carts/view.html"

    def get_object(self, queryset=None):
        self.request.session.set_expiry(0)
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            cart = Cart()
            cart.tax_percentage = 0.075
            cart.save()
            cart_id = cart.id
            # session 생성
            self.request.session["cart_id"] = cart_id
        cart = Cart.objects.get_or_create(id=cart_id)[0]
        # cart 객체가 생성되고, 유저 인증이 일어나기 때문에
        # 로그인 전 생성된 cart 객체는 로그인 후 유지.
        # 반대로 로그인 후 카트를 생성하고, 로그아웃 할 경우
        # cart 객체는 새로 생성됨. -> set_expiry에 의해 logout 또는 브라우저가 닫혔을 때 세션 삭제 됨
        # logout()-> session.flush() 호출
        if self.request.user.is_authenticated:
            cart.user = self.request.user
            cart.save()
        return cart

    def get(self, request):
        cart = self.get_object()
        flash_message = ""
        item_id = request.GET.get("item")
        delete_item = request.GET.get("delete", False)
        item_added = False
        # /?item=item_id
        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            qty = request.GET.get("qty", 1)
            try:
                if int(qty) < 1:
                    delete_item = True
            except:
                raise Http404

            # CartItem = Variation + Cart
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
            # /?item=item_id&delete=True: 해당 아이템 카트에서 비우기
            if created:
                flash_message = "Successfully added to the cart"
                item_added = True
            if delete_item:
                flash_message = "Item removed successfully."
                cart_item.delete()
                # cart.delete()
            # /?item=item_id&qty=qty_number: 카트에 수량만큼 아이템 담기
            else:
                if not created:
                    flash_message = "Quantity has been updated successfully."
                cart_item.quantity = qty
                cart_item.save()

            if not request.is_ajax():
                return HttpResponseRedirect(reverse('cart'))

        if request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total = None
            try:
                subtotal = cart_item.cart.subtotal
            except:
                subtotal = None
            try:
                cart_total = cart_item.cart.total
            except:
                cart_total = None

            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = None

            try:
                total_items = cart_item.cart.items.count()
            except:
                total_items = 0

            data = {
                "deleted": delete_item,
                "item_added": item_added,
                "line_total": total,
                "subtotal": subtotal,
                "cart_total": cart_total,
                "tax_total": tax_total,
                "flash_message": flash_message,
                "total_items": total_items
            }
            return JsonResponse(data)

        context = {
            "object": self.get_object()
        }
        template = self.template_name
        # return HttpResponseRedirect("/")
        return render(request, template, context)


class CheckoutView(CartOrderMixin, FormMixin, DetailView):
    model = Cart
    template_name = "carts/checkout_view.html"
    form_class = GuestCheckoutForm

    def get_order(self, *args, **kwargs):
        cart = self.get_object()
        new_order_id = self.request.session.get("order_id")
        if new_order_id is None:
            new_order = Order.objects.create(cart=cart)
            self.request.session["order_id"] = new_order.id
        else:
            new_order = Order.objects.get(id=new_order_id)
        return new_order

    def get_object(self, *args, **kwargs):
        cart = self.get_cart()
        if cart is None:
            return None
        return cart

    def get_context_data(self, *args, **kwargs):
        # user_checkout = None
        context = super(CheckoutView, self).get_context_data(*args, **kwargs)
        user_can_continue = False
        user_check_id = self.request.session.get("user_checkout_id")
        if self.request.user.is_authenticated:
            user_can_continue = True
            user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)
            user_checkout.user = self.request.user
            user_checkout.save()
            self.request.session["user_checkout_id"] = user_checkout.id
        elif not self.request.user.is_authenticated and user_check_id is None:
            context["login_form"] = AuthenticationForm()
            context["next_url"] = self.request.build_absolute_uri()
        else:
            pass
        if user_check_id is not None:
            user_can_continue = True
        context["order"] = self.get_order()
        context["user_can_continue"] = user_can_continue
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user_checkout, created = UserCheckout.objects.get_or_create(email=email)
            request.session['user_checkout_id'] = user_checkout.id
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("checkout")

    # def get(self, request, *args, **kwargs):
    #     get_data = super(CheckoutView, self).get(request, *args, **kwargs)
    #     cart = self.get_object()
    #     new_order = self.get_order()
    #     user_checkout_id = request.session.get('user_checkout_id')
    #     if user_checkout_id is not None:
    #         user_checkout = UserCheckout.objects.get(id=user_checkout_id)
    #         billing_address_id = request.session.get("billing_address_id")
    #         shipping_address_id = request.session.get("shipping_address_id")
    #
    #         if billing_address_id is None or shipping_address_id is None:
    #             return redirect('order_address')
    #         else:
    #             # billing_address_id & shipping_address_id는 UserAddress에서 생성되기 때문에
    #             # 둘의 id가 중복될 일은 없음
    #             billing_address = UserAddress.objects.get(id=billing_address_id)
                # 이 구조에서 만일
    #             shipping_address = UserAddress.objects.get(id=shipping_address_id)
    #         new_order.user = user_checkout
    #         new_order.billing_address = billing_address
    #         new_order.shipping_address = shipping_address
    #         new_order.save()
    #     return get_data

    def get(self, request, *args, **kwargs):
        get_data = super(CheckoutView, self).get(request, *args, **kwargs)
        cart = self.get_object()
        if cart is None:
            return redirect("cart")
        new_order = self.get_order()
        user_checkout_id = request.session.get("user_checkout_id")
        if user_checkout_id is not None:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            if new_order.billing_address is None or new_order.shipping_address is None:
                return redirect("order_address")
            new_order.user = user_checkout
            new_order.save()
        return get_data
