from .models import Cart

def cart_items_count(request):
    """Add cart items count to context"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {'cart_items_count': cart.cartitem_set.count()}
    return {'cart_items_count': 0}