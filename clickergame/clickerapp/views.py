from django.shortcuts import render, redirect
from .models import Profile
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@login_required
def home(request):
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        score = profile.score
    else:
        score = 0

    return render(request, "home.html", {"score": score})

def about(request):
    return render(request, "about.html")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/accounts/login/")
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})





def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Optional: automatically log user in
            login(request, user)

            return redirect("home")
        else:
            print(form.errors)  # important for debugging
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {
        "form": form
    })

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect("login")



