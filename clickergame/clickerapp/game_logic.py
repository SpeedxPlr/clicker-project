from .models import Profile
from django.http import JsonResponse


score = 0  # temporary (resets when server restarts)


def add_point(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.score +=  profile.points_per_click
    profile.save()

    return JsonResponse({'score': profile.score})

def user_score(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile.score

def get_score(request):
    if not request.user.is_authenticated:
        return JsonResponse({"score": 0})

    return JsonResponse({
        "score": user_score(request.user)
    })


def upgrade_click(request):
    profile = Profile.objects.get(user=request.user)

    cost = profile.points_per_click * 10

    if profile.score >= cost:
        profile.score -= cost
        profile.points_per_click += 1
        profile.save()

        return JsonResponse({
            "success": True,
            "score": profile.score,
            "points_per_click": profile.points_per_click,
            "cost": cost
        })

    return JsonResponse({
        "success": False,
        "error": "Not enough points",
        "cost": cost
    })