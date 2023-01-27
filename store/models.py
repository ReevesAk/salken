from django.db import models
from category.models import Category

# Create your models here.

# Product describes model for each product category.
class Product(models.Model):
    product_name    = models.CharField(max_length=250, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    descriptin      = models.TextField(max_length=300, blank=True)
    price           = models.IntegerField()
    image           = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    added_at        = models.DateField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name