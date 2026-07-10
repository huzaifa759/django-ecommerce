from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if not product.in_stock:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(product.get_absolute_url())

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    current = 0
    existing = cart.cart.get(str(product.id))
    if existing:
        current = existing["quantity"]

    if current + quantity > product.stock:
        messages.error(
            request,
            f"Only {product.stock} of {product.name} available.",
        )
        return redirect(product.get_absolute_url())

    cart.add(product=product, quantity=quantity)
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect("cart:detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} of {product.name} available.")
        return redirect("cart:detail")

    if quantity <= 0:
        cart.remove(product)
        messages.info(request, f"Removed {product.name} from your cart.")
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, "Cart updated.")
    return redirect("cart:detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from your cart.")
    return redirect("cart:detail")
