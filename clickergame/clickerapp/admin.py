from django.contrib import admin
from .models import Profile, Upgrade, ProfileUpgrade

admin.site.register(Profile)
admin.site.register(Upgrade)
admin.site.register(ProfileUpgrade)
