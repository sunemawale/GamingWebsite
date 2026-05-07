from django.contrib import admin
from .models import Product, Order

# Register your models here.
from django.contrib import admin
from .models import Product

admin.site.register(Product)
admin.site.register(Order)