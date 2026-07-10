from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related("category")
    category = None
    query = request.GET.get("q", "").strip()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "catalog/product_list.html",
        {
            "categories": categories,
            "category": category,
            "page_obj": page_obj,
            "query": query,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True,
    )
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)[:4]
    )
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "related": related,
        },
    )
