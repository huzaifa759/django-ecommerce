from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.cart import Cart
from catalog.models import Product

from .models import Order, OrderItem


@login_required
@require_POST
def order_confirm(request):
    cart = Cart(request)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:detail")

    items = list(cart)
    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:detail")

    try:
        with transaction.atomic():
            product_ids = [item["product"].id for item in items]
            products = {
                p.id: p
                for p in Product.objects.select_for_update().filter(id__in=product_ids)
            }

            for item in items:
                product = products.get(item["product"].id)
                if product is None or not product.is_active:
                    raise ValueError(f"{item['product'].name} is no longer available.")
                if item["quantity"] > product.stock:
                    raise ValueError(
                        f"Only {product.stock} of {product.name} available."
                    )

            order = Order.objects.create(
                user=request.user,
                status=Order.Status.CONFIRMED,
            )

            for item in items:
                product = products[item["product"].id]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=item["price"],
                    quantity=item["quantity"],
                )
                product.stock -= item["quantity"]
                product.save(update_fields=["stock", "updated_at"])

            cart.clear()
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("cart:detail")

    messages.success(request, f"Order #{order.pk} confirmed.")
    return redirect("orders:detail", order_id=order.pk)


@login_required
def order_list(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
    )
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        pk=order_id,
        user=request.user,
    )
    return render(request, "orders/order_detail.html", {"order": order})
