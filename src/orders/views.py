# Create your views here.
from django.views.generic import FormView

# from orders.forms import AddressForm
# from orders.models import UserAddress
from orders.forms import AddressForm
from orders.models import UserAddress


class AddressSelectFormView(FormView):
    form_class = AddressForm
    template_name = 'orders/address_select.html'

    def get_form(self, form_class=None):
        form = super(AddressSelectFormView, self).get_form()
        form.fields['billing_address'].queryset = UserAddress.objects.filter(
            user__email=self.request.user.email,
            type='billing',
        )
        # form.fields['billing_address'].queryset = UserAddress.objects.all()
        form.fields['shipping_address'].queryset = UserAddress.objects.filter(
            user__email=self.request.user.email,
            type='shipping',
        )
        # print(form)
        return form

    def form_valid(self, form):
        billing_address = form.cleaned_data['billing_address']
        shipping_address = form.cleaned_data['shipping_address']
        print(billing_address.id)
        # self.request.session[****_address] -> carts.views.CheckoutView
        self.request.session['billing_address_id'] = billing_address.id
        self.request.session['shipping_address_id'] = shipping_address.id
        return super(AddressSelectFormView, self).form_valid(form)

    def get_success_url(self):
        return '/checkout/'
