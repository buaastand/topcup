from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime
from .models import Competition
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
    if 'order' in request.GET:
        order = request.GET['order']
    if 'selected' in request.GET:
        selected = request.GET['selected']

    if selected == '1':
        list = Competition.objects.filter(status=1)
    elif selected == '2':
        list = Competition.objects.filter(status=2)
    else:
        list = Competition.objects.filter(status__gt=0)

    total = len(list)
    if order == '1':
        list.order_by("start_date")
    elif order == '2':
        list.order_by("-finish_date")
    elif order == '3':
        list.order_by("finish_date")
    else:
        list.order_by("-start_date")

    paginator = Paginator(list, 6) # 每页6条

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
    return render(request,"../templates/CompetitionList.html", context)
