from django.contrib.auth import views as account_views
from django.urls import path

import accounts.views as user_views

urlpatterns = [
    path("register/", user_views.register, name="register"),
    path(
        "login/",
        account_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "logout/",
        account_views.LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
]