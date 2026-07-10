from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ("order", "product_name", "price", "quantity")
    search_fields = ("product_name", "order__id")
