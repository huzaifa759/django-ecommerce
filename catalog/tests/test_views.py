import pytest
from django.urls import reverse

from catalog.tests.factories import CategoryFactory, ProductFactory


@pytest.mark.django_db
class TestProductListView:
    def test_lists_active_products(self, client):
        active = ProductFactory(name="Blue T-Shirt", is_active=True)
        ProductFactory(name="Hidden Shirt", is_active=False)

        response = client.get(reverse("catalog:product_list"))

        assert response.status_code == 200
        assert b"Blue T-Shirt" in response.content
        assert b"Hidden Shirt" not in response.content
        assert active in response.context["page_obj"]

    def test_empty_state(self, client):
        response = client.get(reverse("catalog:product_list"))

        assert response.status_code == 200
        assert b"No products found." in response.content

    def test_filters_by_category(self, client):
        shirts = CategoryFactory(name="Shirts", slug="shirts")
        shoes = CategoryFactory(name="Shoes", slug="shoes")
        ProductFactory(name="Blue T-Shirt", category=shirts)
        ProductFactory(name="Running Shoes", category=shoes)

        response = client.get(
            reverse("catalog:category", kwargs={"category_slug": "shirts"})
        )

        assert response.status_code == 200
        assert response.context["category"] == shirts
        assert b"Blue T-Shirt" in response.content
        assert b"Running Shoes" not in response.content
        assert b"Shirts" in response.content

    def test_category_not_found_returns_404(self, client):
        response = client.get(
            reverse("catalog:category", kwargs={"category_slug": "missing"})
        )

        assert response.status_code == 404

    def test_search_filters_by_name_and_description(self, client):
        ProductFactory(name="Blue T-Shirt", description="Soft cotton")
        ProductFactory(name="Red Hat", description="Warm wool")
        ProductFactory(name="Green Socks", description="Blue accents")

        response = client.get(reverse("catalog:product_list"), {"q": "blue"})

        assert response.status_code == 200
        assert response.context["query"] == "blue"
        assert b"Blue T-Shirt" in response.content
        assert b"Green Socks" in response.content
        assert b"Red Hat" not in response.content

    def test_search_within_category(self, client):
        shirts = CategoryFactory(slug="shirts")
        shoes = CategoryFactory(slug="shoes")
        ProductFactory(name="Blue T-Shirt", category=shirts)
        ProductFactory(name="Blue Shoes", category=shoes)

        response = client.get(
            reverse("catalog:category", kwargs={"category_slug": "shirts"}),
            {"q": "blue"},
        )

        assert response.status_code == 200
        assert b"Blue T-Shirt" in response.content
        assert b"Blue Shoes" not in response.content

    def test_pagination(self, client):
        for i in range(9):
            ProductFactory(name=f"Product {i}")

        first_page = client.get(reverse("catalog:product_list"))
        second_page = client.get(reverse("catalog:product_list"), {"page": 2})

        assert first_page.status_code == 200
        assert second_page.status_code == 200
        assert first_page.context["page_obj"].paginator.num_pages == 2
        assert len(first_page.context["page_obj"]) == 8
        assert len(second_page.context["page_obj"]) == 1
        assert b"Previous" in second_page.content
        assert b"Next" in first_page.content

    def test_renders_category_sidebar(self, client):
        CategoryFactory(name="Shirts", slug="shirts")
        CategoryFactory(name="Shoes", slug="shoes")

        response = client.get(reverse("catalog:product_list"))

        assert b"All products" in response.content
        assert b"Shirts" in response.content
        assert b"Shoes" in response.content
        assert b"/products/category/shirts/" in response.content


@pytest.mark.django_db
class TestProductDetailView:
    def test_shows_product_details(self, client):
        category = CategoryFactory(name="Shirts")
        product = ProductFactory(
            name="Blue T-Shirt",
            slug="blue-t-shirt",
            category=category,
            description="A soft cotton shirt",
            price="24.99",
            stock=3,
        )

        response = client.get(product.get_absolute_url())

        assert response.status_code == 200
        assert response.context["product"] == product
        assert b"Blue T-Shirt" in response.content
        assert b"Shirts" in response.content
        assert b"$24.99" in response.content
        assert b"In stock (3)" in response.content
        assert b"A soft cotton shirt" in response.content
        assert b"Add to cart" in response.content

    def test_out_of_stock_product(self, client):
        product = ProductFactory(name="Sold Out Shirt", stock=0)

        response = client.get(product.get_absolute_url())

        assert response.status_code == 200
        assert b"Out of stock" in response.content
        assert b"Add to cart" not in response.content

    def test_inactive_product_returns_404(self, client):
        product = ProductFactory(slug="hidden-shirt", is_active=False)

        response = client.get(
            reverse("catalog:product_detail", kwargs={"slug": product.slug})
        )

        assert response.status_code == 404

    def test_missing_product_returns_404(self, client):
        response = client.get(
            reverse("catalog:product_detail", kwargs={"slug": "does-not-exist"})
        )

        assert response.status_code == 404

    def test_shows_related_products_from_same_category(self, client):
        shirts = CategoryFactory(name="Shirts")
        shoes = CategoryFactory(name="Shoes")
        product = ProductFactory(name="Blue T-Shirt", category=shirts)
        related = ProductFactory(name="Red T-Shirt", category=shirts)
        ProductFactory(name="Running Shoes", category=shoes)
        ProductFactory(name="Inactive Shirt", category=shirts, is_active=False)

        response = client.get(product.get_absolute_url())

        assert response.status_code == 200
        assert list(response.context["related"]) == [related]
        assert b"More in Shirts" in response.content
        assert b"Red T-Shirt" in response.content
        assert b"Running Shoes" not in response.content
        assert b"Inactive Shirt" not in response.content
