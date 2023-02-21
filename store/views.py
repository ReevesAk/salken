from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q


from store.models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id

# Create your views here.

# store handles the logic of what is displayed on the store page as well
# as how it is displayed.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(object_list=products, per_page=1  )
        page    = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:     
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(object_list=products, per_page=6)
        page    = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()    

    context = {
        'products': paged_product,
    }
    return render(request=request, template_name='store.html', context=context)


# product_detail handles the logic of the details displayed about a product as
#  well as how it is displayed.
def product_detail(request):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # cart__cart_id referbeces the Cart model as a foreignkey in CartItem model.
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        return
    except Exception as e:                                
        raise e

    context = {
        'single_product' : single_product,
        'incart'         : in_cart,
    }
    return render(request=request, template_name='store/product_detail.html', context=context)


# search handles the search requests for products made by users.
def search(request):

    # Check if the GET request contains the word 'keyword', and 
    # it if does, save the value in the keyword variable.
    if "keyword" in request.GET:
        keyword = request.GET('keyword')
        if keyword:
            # Q is a django feaure used for combining two or more querysets in a GET request.
            product = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': product,
        'product_count': product_count,
    }
    return render(request=request, template_name='store.html', context=context)
