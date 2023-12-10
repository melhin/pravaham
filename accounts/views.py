# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.forms import UserRegisterForm


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse("posts:lobby"))
    return redirect(reverse("accounts:login"))


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Your account has been created",
            )
            return redirect("posts:lobby")
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {"form": form})
