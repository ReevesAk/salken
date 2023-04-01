from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product


# home handles the logic of what is displayed on the homepage as well
# as how it is displayed.
def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request=request,  template_name='home.html', context=context)