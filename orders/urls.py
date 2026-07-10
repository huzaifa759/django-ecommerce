from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="list"),
    path("confirm/", views.order_confirm, name="confirm"),
    path("<int:order_id>/", views.order_detail, name="detail"),
]
