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

@require_http_methods(["GET"])
def CompetitionFormPost(request):
    response = {}
    try:
        competition_data = Competition(
            title = request.GET.get('title'),
            abstract = request.GET.get('abstract'),
            detail = request.GET.get('detail'),
            rule = request.GET.get('rule'),
        )
        competition_data.save()
        response['msg'] = 'success'
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1

    return JsonResponse(response)
