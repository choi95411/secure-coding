from django.urls import path

from . import views

app_name = "moderation"
urlpatterns = [
    path("reports/products/<int:pk>/", views.report_product, name="report_product"),
    path("reports/users/<str:username>/", views.report_user, name="report_user"),
    path("manage/", views.dashboard, name="dashboard"),
    path("manage/users/<int:pk>/", views.moderate_user, name="moderate_user"),
    path("manage/products/<int:pk>/", views.moderate_product, name="moderate_product"),
]
