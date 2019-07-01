import json

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from competition.models import Competition


# Create your views here.
def CompetitionDetail(request):
    return render(request,"../templates/CompetitionDetail.html")

def CompetitionInit(request):
    return render(request, "../templates/CompetitionInit.html")

@csrf_exempt
def CompetitionFormPost(request):
    
    title = request.POST.get('title')
    abstract = request.POST.get('abstract')
    detail = request.POST.get('detail')
    rule = request.POST.get('rule')
    init_date = request.POST.get('init_date')
    submit_end_date = request.POST.get('submit_end_date')
    check_end_date = request.POST.get('check_end_date')
    review_end_date = request.POST.get('review_end_date')
    defense_end_date = request.POST.get('defense_end_date')
    finish_date = request.POST.get('finish_date')

    preview_img = request.FILES.get('preview_img')
    detail_img = request.FILES.get('detail_img')
    start_appendix = request.FILES.get('start_appendix')



    new_competition = Competition(title = title, abstract = abstract,
                                                detail = detail, rule = rule,
                                                init_date = init_date, 
                                                submit_end_date = submit_end_date,
                                                check_end_date = check_end_date,
                                                review_end_date = review_end_date,
                                                defense_end_date = defense_end_date,
                                                finish_date = finish_date,
                                                preview_img = preview_img,
                                                detail_img = detail_img,
                                                start_appendix = start_appendix,
                                                status = 1,
                                                )

    new_competition.save()


    return HttpResponse('创建成功')
