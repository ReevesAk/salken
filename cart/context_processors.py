from django.db.models import Sum
from django.urls import reverse

from .models import CartItem
from .views import _cart_id


# counter provides cart_count, the number of items in the visitor's cart, for
# the navbar badge. Admin pages are skipped so they don't query the cart or
# start a session.
def counter(request):
    if request.path.startswith(reverse('admin:index')):
        return {}

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))
    cart_count = cart_items.aggregate(total=Sum('quantity'))['total'] or 0
    return dict(cart_count=cart_count)
