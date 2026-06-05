from django.contrib.auth.models import User
from django.db import models



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    points_per_click = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username




class Upgrade(models.Model):
    CLICK_POWER = "click_power"
    AUTO_CLICK = "auto_click"
    ADDITIVE_POWER = "additive_power"
    ADDITIVE_MULTIPLIER = "additive_multiplier"
    GLOBAL_MULTIPLIER = "global_multiplier"


    EFFECT_TYPES = [
        (CLICK_POWER, "Click Power"),
        (AUTO_CLICK, "Auto Click"),
        (ADDITIVE_POWER, "Additive Power"),
        (ADDITIVE_MULTIPLIER, "Additive Multiplier"),
        (GLOBAL_MULTIPLIER, "Global Multiplier"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    base_cost = models.IntegerField()

    base_cost = models.IntegerField()

    cost_multiplier = models.FloatField(default=1.15)

    effect_type = models.CharField(
        max_length=30,
        choices=EFFECT_TYPES
    )

    effect_value = models.FloatField()

    is_repeatable = models.BooleanField(default=True)

    cost_multiplier = models.FloatField(default=1.15)
    
    def get_cost(self, current_level):
        if not self.is_repeatable:
            return self.base_cost

        return int(
            self.base_cost *
            (self.cost_multiplier ** current_level)
    )



class ProfileUpgrade(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)

    class Meta:
        unique_together = ("profile", "upgrade")

