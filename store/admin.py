from django.contrib import admin
from . models import Product

# Register your models here.

# ProductAdmin pre_populates the slug when a product is being added.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'category', 'added_at', 'modified_date')

admin.site.register(Product, ProductAdmin)
