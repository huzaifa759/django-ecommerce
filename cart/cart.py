from decimal import Decimal

from catalog.models import Product

SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(SESSION_KEY)
        if cart is None:
            cart = self.session[SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        if self.cart[product_id]["quantity"] > product.stock:
            self.cart[product_id]["quantity"] = product.stock

        if self.cart[product_id]["quantity"] <= 0:
            self.remove(product)
        else:
            self.cart[product_id]["price"] = str(product.price)
            self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session[SESSION_KEY] = {}
        self.cart = self.session[SESSION_KEY]
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        cart = self.cart.copy()
        for product in products:
            item = cart[str(product.id)].copy()
            item["product"] = product
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def __bool__(self):
        return len(self) > 0

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )
