import json

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime
from .models import Competition
from users.models import Expert
from users.models import Student
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django import forms

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from competition.models import Competition


# Create your views here.
def GetUserIdentitiy(request):
    user_identity = 0
    user_name = ' '
    if request.user.is_authenticated:
        if Expert.objects.filter(user__email=request.user.username):
            user_identity = 1  # 专家
            user_name = Expert.objects.get(user__email=request.user.username).user.email

        elif Student.objects.filter(stu_id=request.user.username):
            user_identity = 2  # 学生
            user_name = Student.objects.get(stu_id=request.user.username).user.email
        else:
            user_identity = 3  # 校团委
            user_name = '校团委'
    else:
        user_identity = 0  # 未登录
    return user_name,user_identity

def CompetitionDetail(request):
    user_name, user_identity = GetUserIdentitiy(request)
    print(GetUserIdentitiy(request))
    cptDetail=Competition.objects.get(id= request.GET['id'])
    context = {'cptDetail':cptDetail}
    temp=datetime.date.today()
    now_time =temp
    if now_time<cptDetail.init_date:
        status_type="0"
    elif now_time<cptDetail.submit_end_date:
        status_type="1"
    elif now_time<cptDetail.check_end_date:
        status_type="2"
    elif now_time<cptDetail.review_end_date:
        status_type="3"
    elif now_time<cptDetail.defense_end_date:
        status_type="4"
    else:
        status_type="5"

    context['status_type']=status_type
    context['useridentity'] = user_identity
    context['username'] = user_name
    return render(request,"../templates/CompetitionDetail.html",context)

def CompetitionList(request):
    order = '0'
    selected = '0'
    total = '0'

    if 'order' in request.GET:
        order = request.GET['order']
    if 'selected' in request.GET:
        selected = request.GET['selected']

    #     身份判断
    user_name, user_identity = GetUserIdentitiy(request)

    if selected == '1':
        cptList = Competition.objects.filter(status=1)
    elif selected == '2':
        cptList = Competition.objects.filter(status=2)
    elif selected == '3':
        cptList = Competition.objects.filter(status=0)
    elif user_identity == 3:
        cptList = Competition.objects.all()
    else:
        cptList = Competition.objects.filter(status__gt=0)

    total = len(cptList)
    if order == '1':
        cptList = cptList.order_by("-init_date")
    elif order == '2':
        cptList = cptList.order_by("finish_date")
    elif order == '3':
        cptList = cptList.order_by("-finish_date")
    else:
        cptList = cptList.order_by("init_date")

    now_time = datetime.date.today()
    for i in cptList:
        if now_time < i.init_date:
            i.status = 0
        elif now_time < i.finish_date:
            i.status = 1
        else:
            i.status = 2
        i.save()

    paginator = Paginator(cptList, 6) # 每页6条
    page = request.GET.get('page')
    contacts = paginator.page(1)
    try:
        contacts = paginator.page(page) # contacts为Page对象！
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    context = {}
    context['contacts'] = contacts
    context['selected'] = selected
    context['order'] = order
    context['total'] = total
    context['useridentity'] = user_identity
    context['username'] = user_name
    return render(request,"../templates/CompetitionList.html", context)

@csrf_exempt
def DeleteCompetition(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        # id= int(temp)
        print(request)
        print(id,type(id))
        try:
            Competition.objects.get(id=id).delete()
        except:
            return JsonResponse({'Message': 0})
        return JsonResponse({'Message': 1})
    return JsonResponse({'Message': "删除比赛信息"})




def CompetitionInit(request):
    user_name, user_identity = GetUserIdentitiy(request)
    context ={}
    context['useridentity'] = user_identity
    context['username'] = user_name
    return render(request, "../templates/CompetitionInit.html",context)

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

    now_time = datetime.date.today().strftime('%Y-%m-%d')
    status = 0

    if (now_time < init_date) :
        status = 0
    elif (now_time < finish_date) :
        status = 1
    else :
        status = 2
    


    try:
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
                                                status = status,
                                                )

        new_competition.save()

        print(new_competition.start_appendix)
    except:
        return JsonResponse({'Message': 0})
    return JsonResponse({'Message': 1})

def CompetitionChange(request):
    return render(request,'../templates/CompetitionChange.html')
