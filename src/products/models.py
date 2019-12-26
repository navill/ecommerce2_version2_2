from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        # self._db: 모델 매니저를 커스터마이징 할 때, 반드시 self._db에 대한 설정이 필요함
        # qs = ProductQuerySet(self.model)
        # qs = qs.using(self._db)
        # return qs
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        # get_queryset()은 ProdutQuerySet을 리턴하기 때문에 active()를 사용할 수 있다.
        return self.get_queryset().active()


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    active = models.BooleanField(default=True)

    # slug
    # inventory

    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    sale_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()


# 1.decorator
@receiver(post_save, sender=Product)
def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.title = 'Default'
        new_var.price = product.price
        new_var.save()


# 2.connector
# post_save.connect(product_post_saved_receiver, sender=Product)

# instance: ProductImage
def image_upload_to(instance, filename):
    title = instance.product.title
    # 첫 이미지 등록 시 instance.id를 불러오지 못하는 이유
    # ProductImage 모델이 저장되기 전에 instance.id를 호출 -> None 반환
    # -> post_save: 저장 시점에 이미 image_upload_to가 실행되버림
    # instance.id==None
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = f"{slug}-{instance.id}.{file_extension}"
    return f"products/{slug}/{new_filename}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # image_upload_to: 함수 호출'()'이 아닌 함수명을 할당
    image = models.ImageField(upload_to=image_upload_to, null=True)

    def __str__(self):
        return self.product.title


@receiver(post_save, sender=ProductImage)
def product_image_save_receiver(sender, instance, created, *args, **kwargs):
    product_image = instance
    print(instance)
    print(sender)
    print(*args)
