from django.shortcuts import render, redirect
from .models import Profile
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



from django.http import JsonResponse

score = 0  # temporary (resets when server restarts)


def add_point(request):
    profile = Profile.objects.get(user=request.user)
    profile.score += 1
    profile.save()

    return JsonResponse({'score': profile.score})

def get_score(request):
    if not request.user.is_authenticated:
        return JsonResponse({"score": 0})

    profile, created = Profile.objects.get_or_create(user=request.user)

    return JsonResponse({"score": profile.score})