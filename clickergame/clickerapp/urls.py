from django.urls import path
from .views import home, about, members, details

urlpatterns = [
    path('', home, name="home_page"),
    path('about', about, name="about_page"),
    path('members', members, name="members_page"),
    path('members/', members, name="members_list"),
    path('member/<int:id>', details, name="member_detail")
]