from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    list_editable = ("price", "stock", "is_active")
