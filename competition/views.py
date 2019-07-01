from django.shortcuts import render

from .models import Competition
# Create your views here.
def CompetitionDetail(request):
    if 'id' in request.GET:
        cptDetail=Competition.objects.get(id= request.GET['id'])
        context = {'cptDetail':cptDetail}
        return render(request,"../templates/CompetitionDetail.html",context)

def CompetitionList(request):
    list = Competition.objects.all()
    context = {}
    context['list'] = list
    return render(request,"../templates/CompetitionList.html", context)
