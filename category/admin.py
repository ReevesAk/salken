from django.contrib import admin
from .models import Category

# Register your models here.

# CategoryAdmin pre_populates the slug when the catergory is being created.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

admin.site.register(Category, CategoryAdmin)
