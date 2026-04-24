from django.urls import path, include
from django.contrib import admin
from . import views
from .views import home, about


urlpatterns = [
    path('', home, name="home_page"),
    path('about', about, name="about_page"),
    path('add/', views.add_point, name='add_point'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('admin/', admin.site.urls),
    path("get-score/", views.get_score, name="get_score"),
]