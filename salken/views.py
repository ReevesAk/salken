from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product


# home handles the logic of what is displayed on the homepage as well
# as how it is displayed.
def home(request):
    products = Product.objects.all().filter(is_available=True)

    product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request=request,  template_name='home.html', context=context)