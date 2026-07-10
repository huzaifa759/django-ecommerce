import pytest
from django.db.models.deletion import ProtectedError

from catalog.models import Category
from catalog.tests.factories import CategoryFactory, ProductFactory


@pytest.mark.django_db
class TestCategory:
    def test_str_representation(self):
        category = CategoryFactory(name="Shirts")
        assert str(category) == "Shirts"

    def test_get_absolute_url(self):
        category = CategoryFactory(slug="shirts")
        assert category.get_absolute_url() == "/products/category/shirts/"

    def test_cannot_delete_category_with_products(self):
        category = CategoryFactory()
        ProductFactory(category=category)

        with pytest.raises(ProtectedError):
            category.delete()

        assert Category.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
class TestProduct:
    def test_str_representation(self):
        product = ProductFactory(name="Blue T-Shirt")
        assert str(product) == "Blue T-Shirt"

    def test_in_stock_true_when_stock_positive(self):
        product = ProductFactory(stock=5)
        assert product.in_stock is True

    def test_in_stock_false_when_stock_zero(self):
        product = ProductFactory(stock=0)
        assert product.in_stock is False

    def test_product_belongs_to_category(self):
        category = CategoryFactory(name="Shoes")
        product = ProductFactory(category=category)
        assert product.category.name == "Shoes"

    def test_category_products_related_name(self):
        category = CategoryFactory()
        product = ProductFactory(category=category)
        assert product in category.products.all()

    def test_get_absolute_url(self):
        product = ProductFactory(slug="blue-t-shirt")
        assert product.get_absolute_url() == "/products/blue-t-shirt/"
