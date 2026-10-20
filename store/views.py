from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q


from store.models import Product, ProductGallery, ReviewRating
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from .forms import ReviewForm
from orders.models import OrderProduct

# Create your views here.

# store handles the logic of what is displayed on the store page as well
# as how it is displayed.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(object_list=products, per_page=1  )
        page    = request.GET.get('page')
        paged_product = paginator.get_page(page)
    else:     
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(object_list=products, per_page=6)
        page    = request.GET.get('page')
        paged_product = paginator.get_page(page)

    context = {
        'products': paged_product,
        'product_count': products.count(),
    }
    return render(request=request, template_name='store/store.html', context=context)


# product_detail handles the logic of the details displayed about a product as
#  well as how it is displayed.
def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_404(
        Product, category__slug=category_slug, slug=product_slug
    )
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(user=request.user, product=single_product).exists()
        orderproduct = OrderProduct.objects.filter(
            user=request.user, product_id=single_product.id
        ).exists()
    else:
        # cart__cart_id referbeces the Cart model as a foreignkey in CartItem model.
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()
        orderproduct = False

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    

    context = {
        'single_product' : single_product,
        'incart'         : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request=request, template_name='store/product_detail.html', context=context)


# search handles the search requests for products made by users.
def search(request):
    products = Product.objects.none()

    # Search only when the GET request contains a non-empty 'keyword'.
    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        # Q is a django feaure used for combining two or more querysets in a GET request.
        products = Product.objects.order_by('-added_at').filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword),
            is_available=True,
        )
    context = {
        'products': products,
        'product_count': products.count(),
    }
    return render(request=request, template_name='store/store.html', context=context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)