from django.urls import path

from . import views

app_name = "chat"
urlpatterns = [
    path("", views.conversation_list, name="list"),
    path("global/", views.global_chat, name="global"),
    path("direct/<str:username>/", views.direct_start, name="direct_start"),
    path("<int:pk>/", views.conversation_detail, name="detail"),
]
