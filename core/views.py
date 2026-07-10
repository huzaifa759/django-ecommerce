from django.shortcuts import render

from catalog.models import Category, Product


def home(request):
    featured = Product.objects.filter(is_active=True).select_related("category")[:6]
    categories = Category.objects.all()[:6]
    return render(
        request,
        "core/home.html",
        {
            "featured": featured,
            "categories": categories,
        },
    )
