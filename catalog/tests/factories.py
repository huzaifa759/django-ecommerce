import factory
from catalog.models import Category , Product

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    description = "A test product"
    price = "19.99"
    stock = 5
    is_active = True