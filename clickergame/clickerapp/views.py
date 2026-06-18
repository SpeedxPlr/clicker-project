from django.shortcuts import render, redirect
from .models import Profile
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import get_upgrade_data


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@login_required
def home(request):
    score = 0
    upgrades = []

    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(
            user=request.user
        )

        score = profile.score

        rank = (
            Profile.objects
            .filter(score__gt=profile.score)
            .count()
            + 1
        )

        upgrades = get_upgrade_data(profile)

    return render(request, "home.html", {
        "score": score,
        "upgrades": upgrades,
        "rank": rank,
    })


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

from .models import Profile
from django.http import JsonResponse
from .services import calculate_player_stats
from django.shortcuts import get_object_or_404

from .models import (
    Profile,
    Upgrade,
    ProfileUpgrade,
)

def add_point(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    stats = calculate_player_stats(profile)

    reward = ((stats["click_power"]+stats["additive_power"]) * stats["additive_multiplier"]) *  stats["global_multiplier"]

    profile.score += int(reward)
    profile.save()

    return JsonResponse({
        'score': profile.score
    })


def user_score(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile.score

def get_score(request):
    if not request.user.is_authenticated:
        return JsonResponse({"score": 0})

    return JsonResponse({
        "score": user_score(request.user)
    })


def get_cost(self, current_level):
    if not self.is_repeatable:
        return self.base_cost

    return int(
        self.base_cost *
        (1.15 ** current_level)
    )

def buy_upgrade(request, upgrade_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Login required"},
            status=401
        )
    
    print("Upgrade requested:", upgrade_id)

    upgrades = Upgrade.objects.all()
    print("Existing upgrades:", list(upgrades))


    profile, _ = Profile.objects.get_or_create(
        user=request.user
    )

    upgrade = get_object_or_404(
        Upgrade,
        id=upgrade_id
    )

    profile_upgrade, _ = (
        ProfileUpgrade.objects.get_or_create(
            profile=profile,
            upgrade=upgrade
        )
    )

    if (
        not upgrade.is_repeatable
        and profile_upgrade.level > 0
    ):
        return JsonResponse(
            {"error": "Already purchased"},
            status=400
        )

    cost = upgrade.get_cost(
        profile_upgrade.level
    )

    if profile.score < cost:
        return JsonResponse(
            {"error": "Not enough points"},
            status=400
        )

    profile.score -= cost
    profile_upgrade.level += 1

    profile.save()
    profile_upgrade.save()

    return JsonResponse({
        "success": True,
        "score": profile.score,
        "level": profile_upgrade.level,
        "cost_paid": cost,
    })


from .models import Profile


def leaderboard(request):
    players = Profile.objects.select_related(
        'user'
    ).order_by('-score')[:100]
    profile = request.user.profile


    rank = (Profile.objects.filter(score__gt=profile.score).count()+1)
    return render(
        request,
        'leaderboard.html',
        {'players': players}
    )
