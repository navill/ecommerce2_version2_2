from decimal import Decimal

from django.conf import settings
from django.db import models
# Create your models here.
from django.db.models.signals import pre_save

from carts.models import Cart


class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.CASCADE)  # not required
    email = models.EmailField(unique=True)  # --> required

    def __str__(self):
        return self.email


ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)


class UserAddress(models.Model):
    user = models.ForeignKey(UserCheckout, on_delete=models.CASCADE)
    type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __str__(self):
        return self.street


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    user = models.ForeignKey(UserCheckout, on_delete=models.CASCADE)
    # foreignkey의 대상이 둘 일 경우, 반드시 related_name 지정
    billing_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name='billing_address')
    shipping_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name='shipping_address')
    shipping_total_price = models.DecimalField(max_digits=50, decimal_places=2, default=5.99)
    order_total = models.DecimalField(max_digits=50, decimal_places=2, )

    def __str__(self):
        return str(self.cart.id)


def order_pre_save(sender, instance, *args, **kwargs):
    shipping_total_price = instance.shipping_total_price
    cart_total = instance.cart.total
    order_total = Decimal(shipping_total_price) + Decimal(cart_total)
    instance.order_total = order_total


pre_save.connect(order_pre_save, sender=Order)
