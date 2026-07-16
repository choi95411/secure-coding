from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.PlatformLoginView.as_view(), name="login"),
    path("logout/", views.PlatformLogoutView.as_view(), name="logout"),
    path("me/", views.mypage, name="mypage"),
    path("me/profile/", views.profile_edit, name="profile_edit"),
    path("me/password/", views.password_change, name="password_change"),
    path("users/<str:username>/", views.public_profile, name="public_profile"),
]
