from django.shortcuts import render
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
    list = Competition.objects.all()
    context = {}
    context['list'] = list
    return render(request,"../templates/CompetitionList.html", context)
