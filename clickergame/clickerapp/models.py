from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    points_per_click = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username