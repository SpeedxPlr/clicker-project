from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("clickerapp.urls")),
    path('admin/', admin.site.urls),
]