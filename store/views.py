from django.shortcuts import render, get_object_or_404
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
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:     
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()    

    context = {
        'products': products,
    }
    return render(request=request, template_name='store.html', context=context)


# product_detail handles the logic of the details displayed about a product as
#  well as how it is displayed.
def product_detail(request):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    context = {
        'single_product' : single_product,
    }
    return render(request=request, template_name='store/product_detail.html', context=context)