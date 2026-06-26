from django.shortcuts import render, redirect
from .models import Profile
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import get_upgrade_data, calculate_ppc, calculate_crystals, collect_offline, calculate_asteroids, serialize_upgrades
from .models import Upgrade
import traceback


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

from .models import Profile
from django.http import JsonResponse
from .services import calculate_player_stats
from django.shortcuts import get_object_or_404

from .models import (
    Profile,
    Upgrade,
    ProfileUpgrade,
)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@login_required
def home(request):
    score = 0
    upgrades = []



    profile = request.user.profile

    earned = collect_offline(profile)

    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(
            user=request.user
        )

        score = profile.score
        ppc = calculate_ppc(profile)

        stats = calculate_player_stats(profile)

        next_crystals = int(
            (calculate_crystals(profile)+stats["crystal_additive"])* stats['crystal_multiplier']
        )

        stats = calculate_player_stats(profile)

        next_asteroids = int(
            calculate_asteroids(profile)
            * stats['asteroid_gain']
        )

        rank = (
            Profile.objects
            .filter(score__gt=profile.score)
            .count()
            + 1
        )

        upgrades = get_upgrade_data(profile)

        normal = []
        prestige = []
        asteroid = []

        for item in upgrades:
            if item['upgrade'].currency == Upgrade.NORMAL:
                normal.append(item)
            elif item['upgrade'].currency == Upgrade.PRESTIGE:
                prestige.append(item)

            elif item['upgrade'].currency == Upgrade.ASTEROID:
                asteroid.append(item)

    return render(request, "home.html", {
        "score": score,
        "upgrades": normal,
        "prestige_upgrades": prestige,
        "asteroid_upgrades": asteroid,
        "prestige_upgrades":prestige,
        "profile":profile,
        "rank": rank,
        'next_crystals':next_crystals,
        "asteroid_upgrades": asteroid,
        "ppc": ppc,
        "score": profile.score,
        "asteroids": profile.asteroids,
        "next_asteroids":calculate_asteroids(profile),
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

def logout_view(request):
    logout(request)
    return redirect("login")

def add_point(request):
    profile = Profile.objects.get(user=request.user)

    reward = calculate_ppc(profile)

    Profile.objects.filter(id=profile.id).update(
        score=F("score") + reward
    )

    profile.refresh_from_db()

    return JsonResponse({
        "score": profile.score,
        "reward": reward,
        "ppc": reward,
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


from django.http import JsonResponse

def upgrades(request):
    profile = request.user.profile
    return JsonResponse({
        "upgrades": serialize_upgrades(profile)
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

    cost = upgrade.get_cost(profile_upgrade.level)

    if upgrade.currency == Upgrade.NORMAL:
        money = profile.score

    elif upgrade.currency == Upgrade.PRESTIGE:
        money = profile.crystals

    elif upgrade.currency == Upgrade.ASTEROID:
        money = profile.asteroids

    if money < cost:

        return JsonResponse({"error":"Not enough currency"})


    if upgrade.currency == Upgrade.NORMAL:
        profile.score -= cost

    elif upgrade.currency == Upgrade.PRESTIGE:
        profile.crystals -= cost

    elif upgrade.currency == Upgrade.ASTEROID:
        profile.asteroids -= cost
    profile_upgrade.level += 1

    stats = calculate_player_stats(profile)

    ppc = calculate_ppc(profile)


    profile.save()
    profile_upgrade.save()


    return JsonResponse({
        "success": True,
        "score": profile.score,
        "crystals":profile.crystals,
        "level": profile_upgrade.level,
        "new_cost": upgrade.get_cost(profile_upgrade.level),
        "ppc": calculate_ppc(profile),
        "new_cost": upgrade.get_cost(profile_upgrade.level),
        "next_crystals":calculate_crystals(profile),
        "upgrades":build_upgrade_json(profile),
        "score": profile.score,
        "asteroids": profile.asteroids,
        "next_asteroids": calculate_asteroids(profile),

    })

def buy_max(request, upgrade_id):

    profile = request.user.profile

    upgrade = get_object_or_404(Upgrade,id=upgrade_id)

    pu,_ = ProfileUpgrade.objects.get_or_create(profile=profile,upgrade=upgrade)

    bought = 0

    while True:

        cost = upgrade.get_cost(
            pu.level
        )

        money = (
            profile.score
            if upgrade.currency==Upgrade.NORMAL
            else profile.crystals
        )

        if money < cost:
            break

        if upgrade.currency==Upgrade.NORMAL:

            profile.score -= cost

        else:
            profile.crystals -= cost

        pu.level += 1

        bought += 1

        if not upgrade.is_repeatable:

            break


    profile.save()
    pu.save()
    return JsonResponse({

    "success": True,

    "score": profile.score,

    "crystals": profile.crystals,

    "ppc": calculate_ppc(profile),

    "next_crystals": calculate_crystals(profile),

    "bought": bought,

    "upgrades": [

        {

            "id": item["upgrade"].id,

            "level": item["level"],

            "cost": item["cost"]

        }

        for item in get_upgrade_data(profile)

    ]

})


from .models import Profile


def leaderboard(request):

    profiles = Profile.objects.order_by("-score")

    players = []

    for profile in profiles:

        stats = calculate_player_stats(profile)

        players.append({

            "profile": profile,

            "stats": stats,

            "ppc": calculate_ppc(profile)

        })

    return render(request, "leaderboard.html", {

        "players": players

    })


def auto_click(request):
    try:
        profile = request.user.profile

        stats = calculate_player_stats(profile)
        ppc = calculate_ppc(profile)

        gained = (
            stats["auto_clicks_per_second"]
            * ppc
            * stats["autoclick_multiplier"]
        )

        profile.score += int(gained)
        Profile.objects.filter(id=profile.id).update(score=F("score") + gained)

        return JsonResponse({
            "success": True,
            "score": profile.score,
            "crystals": profile.crystals,
            "ppc": calculate_ppc(profile),
            "next_crystals": calculate_crystals(profile),
            "upgrades": build_upgrade_json(profile),
            "asteroids": profile.asteroids,
            "next_asteroids": calculate_asteroids(profile),
        })

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "error": str(e),
        }, status=500)

@login_required
def prestige(request):

    profile = request.user.profile

    if profile.score < 10000:
        return JsonResponse({
            "success": False,
            "error": "You need at least 10,000 score to prestige."
        })

    gained = calculate_crystals(profile)


    if gained <= 0:

        return JsonResponse({"error":"Not enough score"})


    profile.crystals += gained


    profile.score = 0


    ProfileUpgrade.objects.filter(profile=profile,upgrade__currency=Upgrade.NORMAL).delete()

    profile.prestige_unlocked = True

    profile.save()

    upgrades = get_upgrade_data(profile)


    return JsonResponse({
        
    "success":True,

    "score":profile.score,

    "crystals":profile.crystals,

    "ppc":calculate_ppc(profile),

    "next_crystals":calculate_crystals(profile),

    "upgrades":build_upgrade_json(profile),

    "score": profile.score,

    "asteroids": profile.asteroids,

    "next_asteroids":calculate_asteroids(profile),

    })

def build_upgrade_json(profile):




    upgrades = get_upgrade_data(profile)

    return [

        {
            "id":item['upgrade'].id,

            "level":item['level'],

            "cost":item['cost']

        }

        for item in upgrades

    ]

from django.db.models import F


@login_required

def calculate_rank(profile):
    return Profile.objects.filter(score__gt=profile.score).count() + 1

def profile(request):
  
    profile = request.user.profile
    for name in dir(profile):
        if "upgrade" in name.lower():
            print(name)
    stats = calculate_player_stats(profile)

    all_upgrades = profile.profileupgrade_set.select_related("upgrade")

    rock_upgrades = all_upgrades.filter(
        upgrade__currency=Upgrade.NORMAL
    )

    crystal_upgrades = all_upgrades.filter(
        upgrade__currency=Upgrade.PRESTIGE
    )

    asteroid_upgrades = all_upgrades.filter(
        upgrade__currency=Upgrade.ASTEROID
    )

    upgrades = profile.profileupgrade_set.select_related("upgrade")

    stats = calculate_player_stats(profile)

    ppc = calculate_ppc(profile)

    rank = calculate_rank(profile) # however you're calculating it


    context = {
        "profile": profile,
        "upgrades": upgrades,
        "ppc": ppc,
        "stats": stats,
        "rank": rank,
        "rock_upgrades":rock_upgrades,

        "crystal_upgrades":crystal_upgrades,

        "asteroid_upgrades":asteroid_upgrades,

    }
    

    return render(request, "profile.html", context)


@login_required
def asteroid_reset(request):

    profile = request.user.profile
    stats = calculate_player_stats(profile)

    gained = int(
        calculate_asteroids(profile)*stats['asteroid_gain']
    )


    if gained <= 0:

        return JsonResponse({

            "error":"Need 1M Rocks"

        })


    profile.asteroids += gained


    profile.asteroid_unlocked = True


    profile.score = 0


    keep = int(profile.crystals*stats['crystal_keep'])
    profile.crystals = keep

    ProfileUpgrade.objects.filter(
    profile=profile,
    upgrade__currency__in=[
        Upgrade.NORMAL,
        Upgrade.PRESTIGE
        ]).delete()



    profile.save()

    return JsonResponse({

        "success":True,

        "score":profile.score,

        "crystals":profile.crystals,

        "asteroids":profile.asteroids,

        "ppc":calculate_ppc(profile),

        "next_crystals":calculate_crystals(profile),

        "next_asteroids":calculate_asteroids(profile),

        "upgrades":serialize_upgrades(profile)

    })
