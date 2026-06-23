# game/services.py

from .models import ProfileUpgrade, Upgrade

def calculate_player_stats(profile):
    stats = {
        'click_power':1,
        'additive_power':0,
        'additive_multiplier':1,
        'global_multiplier':1,


        'auto_clicks_per_second':0,


        'crystal_additive':0,
        'crystal_multiplier':1,


        'prestige_keep_upgrades':0,
        'prestige_keep_score':0,
        'prestige_discount':1,

        'asteroid_gain':1,
        'crystal_keep':0,
        'prestige_keep':0,
        'autoclick_multiplier':1,
        }

    upgrades = ProfileUpgrade.objects.filter(profile=profile)


    for pu in upgrades:
        value = pu.upgrade.effect_value * pu.level

        if pu.upgrade.effect_type == Upgrade.CLICK_POWER:
            stats["click_power"] += value

        elif pu.upgrade.effect_type == Upgrade.AUTO_CLICK:
            stats["auto_clicks_per_second"] += value

        elif pu.upgrade.effect_type == Upgrade.ADDITIVE_POWER:
            stats["additive_power"] += value


        elif pu.upgrade.effect_type == Upgrade.ADDITIVE_MULTIPLIER:
            stats["additive_multiplier"] += value


        elif pu.upgrade.effect_type == Upgrade.GLOBAL_MULTIPLIER:
            stats["global_multiplier"] *= (1 + pu.upgrade.effect_value) ** pu.level
        
        elif pu.upgrade.effect_type == Upgrade.CRYSTAL_ADDITIVE:
            stats["crystal_additive"] += value

        elif pu.upgrade.effect_type == Upgrade.CRYSTAL_MULTIPLIER:
            stats["crystal_multiplier"] *= ((1 + pu.upgrade.effect_value)** pu.level)

        elif pu.upgrade.effect_type == Upgrade.ASTEROID_GAIN:
            stats['asteroid_gain'] *= (1 +pu.upgrade.effect_value)**pu.level

        elif pu.upgrade.effect_type == Upgrade.CRYSTAL_KEEP:
            stats['crystal_keep'] += (pu.upgrade.effect_value*pu.level)
        elif pu.upgrade.effect_type == Upgrade.PRESTIGE_KEEP:
            stats['prestige_keep'] += (pu.upgrade.effect_value*pu.level)

    return stats

def get_upgrade_data(profile):
    upgrades = Upgrade.objects.all()

    upgrade_data = []

    for upgrade in upgrades:
        pu, _ = ProfileUpgrade.objects.get_or_create(
            profile=profile,
            upgrade=upgrade
        )

        upgrade_data.append({
            'upgrade': upgrade,
            'level': pu.level,
            'cost': upgrade.get_cost(pu.level)
        })

    return upgrade_data

def calculate_ppc(profile):
    stats = calculate_player_stats(profile)

    return int(
        (
            stats["click_power"]
            + stats["additive_power"]
        )
        * stats["additive_multiplier"]
        * stats["global_multiplier"]
    )

import math


def calculate_prestige(score):
    score = max(score,0)
    return int(
        10 * (score/10000)**0.75
    
    )

def calculate_crystals(profile):

    stats = calculate_player_stats(profile)


    base = calculate_prestige(
        profile.score
    )


    crystals = (

        (base + stats["crystal_additive"])

        *

        stats["crystal_multiplier"]

    )


    return int(crystals)

from django.utils.timezone import now


def collect_offline(profile):

    stats = calculate_player_stats(profile)

    aps = stats["auto_clicks_per_second"]

    current = now()

    elapsed = (
        current
        - profile.last_collected
    ).total_seconds()

    earned = int(

        aps * elapsed

    )


    profile.score += earned


    profile.last_collected = current


    profile.save()


    return earned

def calculate_asteroids(score):

    if score < 1_000_000:
        return 0


    return int(5 * math.sqrt(score / 1_000_000))

def serialize_upgrades(profile):

    return [

        {

            "id": item["upgrade"].id,

            "level": item["level"],

            "cost": item["cost"]

        }

        for item in get_upgrade_data(profile)

    ]