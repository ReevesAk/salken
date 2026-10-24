import logging

from django.http import Http404
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


from store.models import Product, Variation
from . models import Cart, CartItem

logger = logging.getLogger(__name__)


# Create your views here.

# cart_id takes in session id in form of cart_id.
def _cart_id(request):
    if not request.session.session_key:
        # create() sets session_key but returns None.
        request.session.create()
    return request.session.session_key

# _resolve_variations returns the product variations selected in the
# request body, ignoring keys that do not match an active variation.
def _resolve_variations(request, product):
    product_variation = []
    if request.method == "POST":
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
            except Variation.DoesNotExist:
                continue
            product_variation.append(variation)
    return product_variation


# _get_owner_filter returns the lookup that scopes cart items to the
# current visitor: the user when logged in, otherwise the session cart.
def _get_owner_filter(request, create=False):
    if request.user.is_authenticated:
        return {'user': request.user}
    if create:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    return {'cart': cart}


# add_to_cart adds an item to cart whether or not the user has an account.
# Anonymous visitors are tracked through their session key. Adding a product
# with the same variations as an existing cart item increments its quantity.
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = _resolve_variations(request, product)
    owner = _get_owner_filter(request, create=True)

    wanted = {variation.id for variation in product_variation}
    for item in CartItem.objects.filter(product=product, **owner):
        if set(item.variation.values_list('id', flat=True)) == wanted:
            item.quantity += 1
            item.save()
            return redirect('cart')

    item = CartItem.objects.create(product=product, quantity=1, **owner)
    if product_variation:
        item.variation.add(*product_variation)
    return redirect('cart')


# remove_from_cart decrements a cart item, deleting it when it reaches zero.
def remove_from_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        owner = _get_owner_filter(request)
        cart_item = CartItem.objects.get(product=product, id=cart_item_id, **owner)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        logger.warning(
            'remove_from_cart: no cart item %s for product %s', cart_item_id, product_id
        )
        return redirect('cart')

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


# remove_cart_item handles the removal of a card item from the cart.
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        owner = _get_owner_filter(request)
    except Cart.DoesNotExist:
        raise Http404('Cart not found')
    cart_item = get_object_or_404(CartItem, product=product, id=cart_item_id, **owner)
    cart_item.delete()
    return redirect('cart')


# cart handles the GET request for cart details, such as total, 
# quantity, cart_items, tax and grand_total.
def cart(request, total=0, quantity=0, cart_item=None):
    tax = 0
    grand_total = 0
    cart_items = CartItem.objects.none()
    try:
        # this block displays cart view for logged in users.
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:    
            # this block displays cart view for non-logged in users.
            cart = Cart.objects.get(cart_id=_cart_id(request))
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


# checkout handles the GET request for checkout of cart items.
@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    cart_items = CartItem.objects.none()
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax'       : tax,
        'grand_total': grand_total,
    }

    return render(request=request, template_name='store/checkout.html', context=context)    
