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
        next_crystals = calculate_crystals(profile)
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
        "next_asteroids": calculate_asteroids(profile.score),
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

    reward = calculate_ppc(profile)

    profile.score += reward
    profile.save()

    return JsonResponse({
    'score': profile.score,

    'reward': reward,

    'ppc': calculate_ppc(profile),

    'crystals': profile.crystals,

    'next_crystals': calculate_crystals(profile),

    'upgrades': build_upgrade_json(profile),
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
        "upgrades":build_upgrade_json(profile)

    })

def buy_max(request, upgrade_id):

    profile = request.user.profile


    upgrade = get_object_or_404(

        Upgrade,

        id=upgrade_id

    )


    pu,_ = ProfileUpgrade.objects.get_or_create(

        profile=profile,

        upgrade=upgrade

    )


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


def auto_click(request):
    profile = request.user.profile

    stats = calculate_player_stats(profile)

    ppc = calculate_ppc(profile)

    gained = (stats["auto_clicks_per_second"]*stats["autoclick_multiplier"])

    profile.score += int(gained)
    profile.save()

    return JsonResponse({
    "success": True,
    "score": profile.score,
    "crystals": profile.crystals,
    "ppc": calculate_ppc(profile),
    "next_crystals": calculate_crystals(profile),
    "upgrades": build_upgrade_json(profile),
    })

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

    "upgrades":build_upgrade_json(profile)

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

@login_required
def asteroid_reset(request):

    profile = request.user.profile
    stats = calculate_player_stats(profile)

    gained = int(
        calculate_asteroids(profile.score)*stats['asteroid_gain']
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

        "next_asteroids":calculate_asteroids(profile.score),

        "upgrades":serialize_upgrades(profile)

    })
