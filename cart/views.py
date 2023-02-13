from django.shortcuts import render, redirect
from store.models import Product
from . models import Cart, CartItem
from django.shortcuts import get_object_or_404

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


# remove_from_cart removes a product item from the cart.
def remove_from_cart (request, product_id):
    cart = Cart.objects.get(cart_id=cart_id(request))    
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save(self)
    else:
        cart_item.delete(self)
    return redirect('cart')    


# remove_cart_item handles the removal of a card item from the cart.
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete(self)
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_item=None):
    try:
        cart = Cart.objects.get(cart_id=_card_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (24 * total) / 100
        grand_total = total + tax
    except ObjectNotExist:
        pass    


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request=request, template_name='store/cart.html', context=context)
