# game/services.py

from .models import ProfileUpgrade, Upgrade

def calculate_player_stats(profile):
    stats = {
        "click_power": 1,
        "auto_clicks_per_second": 0,
        'additive_power':0,
        "additive_multiplier": 1.0,
        "global_multiplier": 1.0,
        
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
            stats["global_multiplier"] *= (1+value)

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
