from django.shortcuts import render
from .models import Member


def home(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def members(request):
    members = Member.objects.all().values()
    return render(request, "members.html", { "members" : members })

def details(request, id):
    member = Member.objects.get(id=id)
    return render(request, "detail.html", { "member" : member })
