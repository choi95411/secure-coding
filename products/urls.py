from django.urls import path

from . import views

app_name = "products"
urlpatterns = [
    path("", views.product_list, name="list"),
    path("products/new/", views.product_create, name="create"),
    path("products/mine/", views.my_products, name="mine"),
    path("products/<int:pk>/", views.product_detail, name="detail"),
    path("products/<int:pk>/edit/", views.product_update, name="update"),
    path("products/<int:pk>/delete/", views.product_delete, name="delete"),
]
