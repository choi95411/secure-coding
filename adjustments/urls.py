from django.urls import path

from . import views

app_name = "adjustments"
urlpatterns = [
    path("", views.adjustment_list, name="list"),
    path("new/", views.adjustment_create, name="create"),
]
