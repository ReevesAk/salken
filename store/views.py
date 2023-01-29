from django.shortcuts import render
from store.models import Product
from category.models import Category

# Create your views here.

# store handles the logic of what is displayed on the store page as well
# as how it is displayed.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = products.objetcs.filter(category=categories, is_available=True )
        product_count = products.count()
    else:     
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()    

    context = {
        'products': products,
    }
    return render(request, template_name='store/store.html', context=context)