import json

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
import datetime
from .models import Competition
from users.models import Expert
from users.models import Student
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django import forms
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from competition.models import Competition,CompetitionRegistration
from techworks.models import WorkInfo
from django.forms.models import model_to_dict
from competition.models import Competition
from django.views.generic.base import View
from techworks.models import Appendix

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
    cptDetail=Competition.objects.get(id= request.GET['id'])
    context = {'cptDetail':cptDetail}

    temp=datetime.date.today()
    now_time =temp
    if now_time<cptDetail.init_date:
        status_type="-1"
    elif now_time<cptDetail.submit_end_date:
        status_type="0"
    elif now_time<cptDetail.check_end_date:
        status_type="1"
    elif now_time<cptDetail.review_end_date:
        status_type="2"
    elif now_time<cptDetail.defense_end_date:
        status_type="3"
    else:
        status_type="4"

    context['status_type']=status_type
    context['useridentity'] = user_identity
    context['username'] = user_name

    WORKTYPE_MAP = {
        1: "科技发明制作",
        2: "调查报告和学术论文"
    }
    FIELD_MAP = {
        1: "A",
        2: "B",
        3: "C",
        4: "D",
        5: "E",
        6: "F",
    }
    defenseWorkList = WorkInfo.objects.filter(Q(if_defense=1)&Q(registration__competition=cptDetail))
    # defenseWorkList=WorkInfo.objects.filter(if_defense=1,registration)
    defense_WorkList_ret = []
    for i in defenseWorkList:
        defense_WorkList_ret.append(
            {
                'work_id': i.work_id,
                'title': i.title,
                'work_type': WORKTYPE_MAP[i.work_type],
                'field': FIELD_MAP[i.field],
            }
        )
    context['defenseworklist']=defense_WorkList_ret
    return render(request,"../templates/CompetitionDetail.html",context)

def WorkdefenseChange(request):
    work_id = json.loads(request.body)
    Work=WorkInfo.objects.get(work_id=work_id['workid'])
    Work.if_defense=0
    Work.save()
    return JsonResponse({'Message': 1})

def CompetitionUpdate():
    cptList = Competition.objects.all()
    now_time = datetime.date.today()
    for i in cptList:
        if now_time < i.init_date:
            i.status = 0
        elif now_time < i.finish_date:
            i.status = 1
        else:
            i.status = 2
        i.save()

def CompetitionList(request):
    order = '0'
    selected = '0'
    total = '0'

    CompetitionUpdate()

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
    else:
        cptList = Competition.objects.all()

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
    context['username'] = user_name
    return render(request,"../templates/CompetitionList.html", context)

@csrf_exempt
def DeleteCompetition(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        # id= int(temp)
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
    
    print(detail_img)
    if detail_img is None:
        detail_img = 'competition/img/detailimg.jpg'
    
    print(detail_img)
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

@csrf_exempt
def CompetitionChange(request):
    user_name, user_identity = GetUserIdentitiy(request)
    context = {}
    cptDetail = Competition.objects.get(id = request.GET['cptid'])

    temp = datetime.date.today()
    now_time = temp
    if now_time < cptDetail.init_date:
        status_type = "-1"
    elif now_time < cptDetail.submit_end_date:
        status_type = "0"
    elif now_time < cptDetail.check_end_date:
        status_type = "1"
    elif now_time < cptDetail.review_end_date:
        status_type = "2"
    elif now_time < cptDetail.defense_end_date:
        status_type = "3"
    else:
        status_type = "4"

    print(cptDetail.init_date)

    context = {'cptDetail': cptDetail}
    context['username'] = user_name
    context['useridentity'] = user_identity
    context['status_type'] = status_type

    return render(request,'../templates/CompetitionChange.html', context)

@csrf_exempt
def CompetitionChangePost(request):

    cptDetail = Competition.objects.get(id = request.GET['cptid'])
    init_date = request.POST.get('init_date')
    submit_end_date = request.POST.get('submit_end_date')
    check_end_date = request.POST.get('check_end_date')
    review_end_date = request.POST.get('review_end_date')
    defense_end_date = request.POST.get('defense_end_date')
    finish_date = request.POST.get('finish_date')

    print(init_date)
    print(type(init_date))

    try:
        # cptDetail.init_date = init_date
        # cptDetail.submit_end_date = submit_end_date
        # cptDetail.check_end_date = check_end_date
        # cptDetail.review_end_date = review_end_date
        # cptDetail.defense_end_date = defense_end_date
        # cptDetail.finish_date = finish_date

        cptDetail.init_date = datetime.datetime.strptime(init_date, "%Y-%m-%d")
        cptDetail.submit_end_date = datetime.datetime.strptime(submit_end_date, "%Y-%m-%d")
        cptDetail.check_end_date = datetime.datetime.strptime(check_end_date, "%Y-%m-%d")
        cptDetail.review_end_date = datetime.datetime.strptime(review_end_date, "%Y-%m-%d")
        cptDetail.defense_end_date = datetime.datetime.strptime(defense_end_date, "%Y-%m-%d")
        cptDetail.finish_date = datetime.datetime.strptime(finish_date, "%Y-%m-%d")
        cptDetail.save()
    except:
        return JsonResponse({'Message': 0})
    return JsonResponse({'Message': 1})

class CompetitionFinalResult(View):

    def get(self, request):
        competition_id = request.GET.get('id', 45)
        competition = Competition.objects.get(id=competition_id)
        appendix = []
        try:
            name = competition.end_appendix.name
            name_list = competition.end_appendix.name.split('/')
            appendix.append({"name": name_list[len(name_list) - 1], "url": competition.end_appendix.url})
        except:
            name = ''
            competition.end_appendix.delete()
            competition.save()
        return render(request, 'final_result.html', {'id': competition_id, 'detail': competition.result_details,
                                                     'appendix': appendix})
        # try:
        #
        # except:
        #     return JsonResponse({'message':'找不到比赛'})

    def post(self, request):
        try:
            with transaction.atomic():
                competition_id = request.POST.get('id')
                competition = Competition.objects.get(id=competition_id)
                competition.result_details = request.POST.get('detail')
                try:
                    name = competition.end_appendix.name
                    competition.end_appendix.delete()
                    competition.save()
                except:
                    name = ''
                competition.end_appendix = request.FILES.get('end_appendix')
                competition.save()
            return JsonResponse({'message':'SUCCESS'})
        except:
            return JsonResponse({'message':'ERROR'})


