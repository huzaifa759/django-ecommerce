from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Category, Product


DEMO_DATA = [
    {
        "category": "Kitchen",
        "products": [
            {
                "name": "Cast Iron Skillet",
                "price": "42.00",
                "stock": 12,
                "description": "10-inch skillet that holds heat well for searing and baking.",
            },
            {
                "name": "Wooden Cutting Board",
                "price": "28.50",
                "stock": 20,
                "description": "Thick maple board with a juice groove along one side.",
            },
            {
                "name": "Ceramic Pour-Over Set",
                "price": "34.00",
                "stock": 8,
                "description": "Dripper and mug baked in the same glaze; fits standard filters.",
            },
        ],
    },
    {
        "category": "Desk",
        "products": [
            {
                "name": "Notebook (A5)",
                "price": "9.00",
                "stock": 40,
                "description": "Dotted pages, lay-flat binding, sturdy enough for daily notes.",
            },
            {
                "name": "Desk Lamp",
                "price": "39.00",
                "stock": 15,
                "description": "Warm LED with an adjustable arm; plugs into a standard outlet.",
            },
            {
                "name": "Cable Tray",
                "price": "18.00",
                "stock": 22,
                "description": "Under-desk tray that keeps power strips off the floor.",
            },
        ],
    },
    {
        "category": "Outdoors",
        "products": [
            {
                "name": "Reusable Water Bottle",
                "price": "22.00",
                "stock": 30,
                "description": "750 ml insulated bottle that keeps drinks cold for hours.",
            },
            {
                "name": "Canvas Tote",
                "price": "16.00",
                "stock": 25,
                "description": "Heavy canvas tote with an inner pocket for keys or a phone.",
            },
            {
                "name": "Compact Rain Jacket",
                "price": "55.00",
                "stock": 0,
                "description": "Packable shell with taped seams — currently between shipments.",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed demo categories and products for local learning."

    def handle(self, *args, **options):
        created_categories = 0
        created_products = 0

        for group in DEMO_DATA:
            category, cat_created = Category.objects.get_or_create(
                slug=slugify(group["category"]),
                defaults={"name": group["category"]},
            )
            if cat_created:
                created_categories += 1

            for item in group["products"]:
                slug = slugify(item["name"])
                _, prod_created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "category": category,
                        "name": item["name"],
                        "description": item["description"],
                        "price": item["price"],
                        "stock": item["stock"],
                        "is_active": True,
                    },
                )
                if prod_created:
                    created_products += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_categories} categories, "
                f"{created_products} products created."
            )
        )
