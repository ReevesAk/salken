from django.shortcuts import render, redirect
from store.models import Product
from . models import Cart, CartItem

# Create your views here.

# cart_id takes in session id in form of cart_id.
def cart_id(request):
    cart = request.session_key
    if not cart:
        cart = request.session_create()
    return cart

# add_to_cart adds an item to cart whether or not the user has an account.
# It maks use of coookie session keys.
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id) # This gets the products from the store.
    try:
        cart = Cart.objects.get(cart_id=cart_id(request)) # get the cart using the cart_id present in the session.
    except Cart.DoesNotExist:
        cart =  Cart.objects.create(
            cart_id=cart_id(request)
        )
        cart.save()    

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1 # Increment cart_item.
        cart_item.save(self)
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1, 
            cart=cart,
        )
        cart_item.save(self)    
    return redirect('cart')

def cart(request):
    return render(request=request, template_name='store/cart.html')