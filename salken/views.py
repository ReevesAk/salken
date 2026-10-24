from django.shortcuts import render
from store.models import Product


# home handles the logic of what is displayed on the homepage as well
# as how it is displayed.
def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('added_at')

    context = {
        'products': products,
    }
    return render(request=request, template_name='home.html', context=context)
