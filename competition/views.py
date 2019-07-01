from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime
from .models import Competition
from users.models import Expert
from users.models import Student
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# Create your views here.
def CompetitionDetail(request):
    if 'id' in request.GET:
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
        return render(request,"../templates/CompetitionDetail.html",context)

def CompetitionList(request):
    order = 0
    selected = 0
    total = 0
    user_identity = 0

    if 'order' in request.GET:
        order = request.GET['order']
    if 'selected' in request.GET:
        selected = request.GET['selected']
    if request.user.is_authenticated:
        if Expert.objects.filter(name=request.user.username):
            user_identity = 1 #专家
        elif Student.objects.filter(name=request.user.username):
            user_identity = 2 #学生
        else:
            user_identity = 3 #校团委
    else:
        user_identity = 0 #未登录

    if selected == '1':
        cptList = Competition.objects.filter(status=1)
    elif selected == '2':
        cptList = Competition.objects.filter(status=2)
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

