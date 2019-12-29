from decimal import Decimal

from django.conf import settings
from django.db import models
# Create your models here.
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from products.models import Variation


class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    item = models.ForeignKey(Variation, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # instance.save() 되기 전, receiver(pre_save)에 의해 제품 수량에 맞는 가격으로 업데이
    line_item_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item.title

    def remove(self):
        # Variation.remove_from_cart()
        return self.item.remove_from_cart()


# CartItem 저장 전, 수량에 따른 아이템 가격 갱신
@receiver(pre_save, sender=CartItem)
def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if int(qty) >= 1:
        price = instance.item.get_price()
        line_item_total = Decimal(qty) * Decimal(price)
        instance.line_item_total = line_item_total


# CartItem이 저장된 후, Cart의 update_subtotal() 메서드를 호출하여 cart.subtotal 갱신
@receiver([post_save, post_delete], sender=CartItem)
def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
    instance.cart.update_subtotal()


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    items = models.ManyToManyField(Variation, through=CartItem)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subtotal = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
    tax_percentage = models.DecimalField(max_digits=10, decimal_places=5, default=0.085)
    tax_total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
    total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)

    def __str__(self):
        return str(self.id)

    def update_subtotal(self):
        print("updating...")
        subtotal = 0
        items = self.cartitem_set.all()
        for item in items:
            subtotal += item.line_item_total
            self.subtotal = "%.2f" % (subtotal)
        self.save()


@receiver(pre_save, sender=Cart)
def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
    subtotal = Decimal(instance.subtotal)
    tax_total = round(subtotal * Decimal(instance.tax_percentage), 2)  # 8.5%
    # print(instance.tax_percentage)
    total = round(subtotal + Decimal(tax_total), 2)
    # 세금
    instance.tax_total = "%.2f" % (tax_total)
    # 세금을 포함한 총 금액
    instance.total = "%.2f" % (total)
