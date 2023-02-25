from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist


from store.models import Product, Variation
from . models import Cart, CartItem


# Create your views here.

# cart_id takes in session id in form of cart_id.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# add_to_cart adds an item to cart whether or not the user has an account.
# It maks use of coookie session keys.
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id) # This gets the products from the store.
    product_variation = []
    if request.method == "POST":
        # loop through the request body and collect dynamic variation types.
       for item in request.POST:
           key = item
           value = request.POST[key]

           try:
               variation =  Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
               product_variation.append(variation)
           except:
                pass

    try:
        cart = Cart.objects.get(cart_id=cart_id(request)) # get the cart using the cart_id present in the session.
    except Cart.DoesNotExist:
        cart =  Cart.objects.create(
            cart_id=cart_id(request)
        )
        cart.save()    

    cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # existing_variations -> database
        # current variation -> product_variation
        # item_id -> database

        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variations = item.variations.all()
            ex_var_list.append(existing_variations)
            id.append(item.id)

        if product_variation in ex_var_list:
            # increase the cart item quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()

        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variation.clear()
                item.variation.add(*product_variation)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1, 
            cart=cart,
        )
        # add varitaion in a cart item.
        if len(product_variation) > 0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save()    
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
        tax = 0, # Initialise tax to bypass error.
        grand_total = 0. # Initialise grand_total to bypass error.
        cart = Cart.objects.get(cart_id=_card_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (24 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass    


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request=request, template_name='store/cart.html', context=context)
