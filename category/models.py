from django.db import models

# Create your models here.

# Category describes model for product category.
class Category(models.Model):
    catergory_name = models.CharField(max_length=50, unique=True)
    slug           = models.CharField(max_length=100, unique=True)
    description    = models.TextField(max_length=255, blank=True)
    category_img   = models.ImageField(upload_to="photos/categories", blank=True) # Saves photo to the specified path.

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.catergory_name
