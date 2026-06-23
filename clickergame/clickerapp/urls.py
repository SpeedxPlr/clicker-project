from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from .views import  about, register_view
from django.views.generic.base import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/home")),
    path('home', views.home, name="home"),
    path('about', about, name="about_page"),
    path('add/', views.add_point, name='add_point'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name= 'logout'),
    path('admin/', admin.site.urls),
    path("get-score/", views.get_score, name="get_score"),
    path("buy-upgrade/<int:upgrade_id>/",views.buy_upgrade,name="buy_upgrade"),
    path("accounts/register/", register_view, name="register"),
    path('leaderboard/',views.leaderboard,name='leaderboard'),
    path("auto-click/",views.auto_click,name="auto_click"),
    path("prestige/",views.prestige,name="prestige"),
    path("asteroid-reset/",views.asteroid_reset,name="asteroid_reset"),
    path("buy-max/<int:upgrade_id>/",views.buy_max,name="buy_max")
]