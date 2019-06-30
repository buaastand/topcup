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

@require_http_methods(["POST"])
def CompetitionFormPost(request):
    response = {}
    try:
        cptdata = Competition(title = request.POST.get('title'),
                                abstract = request.POST.get('abstract'),
                                rule = request.POST.get('rule'),
                                detail = request.POST.get('detail'),
                                init_date = request.POST.get('init_date'),
                                submit_end_date = request.POST.get('submit_end_date'),
                                check_end_date = request.POST.get('check_end_date'),
                                review_end_date = request.POST.get('review_end_date'),
                                defense_end_date = request.POST.get('defense_end_date'),
                                finish_date = request.POST.get('finish_date'))
        cptdata.save()
        response['msg'] = 'success'
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1

    return JsonResponse(response)
