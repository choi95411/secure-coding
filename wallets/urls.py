from django.urls import path

from . import views

app_name = "wallets"
urlpatterns = [
    path("", views.wallet_detail, name="detail"),
    path("transfer/", views.transfer_create, name="transfer"),
]
