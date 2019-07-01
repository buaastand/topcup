from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
from competition.models import Competition

import json

# Create your views here.
def CompetitionDetail(request):
    return render(request,"../templates/CompetitionDetail.html")

def CompetitionInit(request):
    return render(request, "../templates/CompetitionInit.html")

def CompetitionFormPost(request):
    data = {}
    data['title'] = request.POST('title')
    return render(request, '')
