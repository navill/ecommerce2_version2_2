from django.http import Http404
from django.shortcuts import get_object_or_404, render
# Create your views here.
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin

from carts.models import CartItem, Cart
from products.models import Variation


class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = "carts/view.html"

    def get_object(self, queryset=None):
        self.request.session.set_expiry(0)
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            cart = Cart()
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
        item_id = request.GET.get("item")
        delete_item = request.GET.get("delete")
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
            cart_item = CartItem.objects.get_or_create(cart=cart, item=item_instance)[0]
            # /?item=item_id&delete=True: 해당 아이템 카트에서 비우기
            if delete_item:
                cart_item.delete()
                cart.delete()
            # /?item=item_id&qty=qty_number: 카트에 수량만큼 아이템 담기
            else:
                cart_item.quantity = qty
                cart_item.save()
        # /?delete=True: 카트 비우기
        elif delete_item:
            cart.delete()

        context = {
            "object": self.get_object()
        }
        template = self.template_name
        # return HttpResponseRedirect("/")
        return render(request, template, context)
