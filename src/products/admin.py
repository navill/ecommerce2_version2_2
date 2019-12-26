from django.contrib import admin

# Register your models here.
from products.models import *

admin.site.register(Product)
admin.site.register(Variation)
admin.site.register(ProductImage)
