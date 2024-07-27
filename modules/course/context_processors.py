from .models import Cart


def cart_context(request):
    total_quantity = 0
    total_price = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
        total_price = sum(item.quantity * item.product.price for item in cart_items)

    return {
        'total_quantity': total_quantity,
        'total_price': total_price,
    }
