# Create your views here.
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import FormView, CreateView, DetailView, ListView

# from orders.forms import AddressForm
# from orders.models import UserAddress
from orders.forms import AddressForm, UserAddressForm
from orders.mixin import LoginRequiredMixin, CartOrderMixin
from orders.models import UserAddress, UserCheckout, Order


class OrderDetail(DetailView):
    model = Order

    def dispatch(self, request, *args, **kwargs):
        try:
            user_check_id = self.request.session.get("user_checkout_id")
            user_checkout = UserCheckout.objects.get(id=user_check_id)
        except UserCheckout.DoesNotExist:
            user_checkout = UserCheckout.objects.get(user=request.user)
        except:
            user_checkout = None

        obj = self.get_object()
        if obj.user == user_checkout and user_checkout is not None:
            return super(OrderDetail, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


class UserAddressCreateView(CreateView):
    form_class = UserAddressForm
    template_name = "forms.html"
    success_url = "/checkout/address/"

    def get_checkout_user(self):
        user_check_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        return user_checkout

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.get_checkout_user()
        return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)


class OrderList(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()

    def get_queryset(self):
        user_check_id = self.request.user.id
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        return super(OrderList, self).get_queryset().filter(user=user_checkout)


class AddressSelectFormView(CartOrderMixin, FormView):
    form_class = AddressForm
    template_name = 'orders/address_select.html'

    def dispatch(self, *args, **kwargs):  # 1
        b_address, s_address = self.get_addresses()
        if b_address.count() == 0:
            messages.success(self.request, "Please add a billing address before continuing")
            return redirect("user_address_create")
        elif s_address.count() == 0:
            messages.success(self.request, "Please add a shipping address before continuing")
            return redirect("user_address_create")
        else:
            return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

    def get_addresses(self, *args, **kwargs):  # 2
        user_check_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        b_address = UserAddress.objects.filter(
            user=user_checkout,
            type='billing',
        )
        print('get_address: ', b_address)
        s_address = UserAddress.objects.filter(
            user=user_checkout,
            type='shipping',
        )
        print('get_address: ', s_address)
        return b_address, s_address

    def get_form(self, *args, **kwargs):  # 3
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        b_address, s_address = self.get_addresses()
        form.fields["billing_address"].queryset = b_address
        form.fields["shipping_address"].queryset = s_address
        print('get_form: ', self.get_addresses())
        return form

    def form_valid(self, form):
        billing_address = form.cleaned_data['billing_address']
        shipping_address = form.cleaned_data['shipping_address']
        # self.request.session[****_address] -> carts.views.CheckoutView
        # self.request.session['billing_address_id'] = billing_address.id
        # self.request.session['shipping_address_id'] = shipping_address.id
        order = self.get_order()
        order.billing_address = billing_address
        order.shipping_address = shipping_address
        order.save()
        return super(AddressSelectFormView, self).form_valid(form)

    def get_success_url(self):
        return '/checkout/'
