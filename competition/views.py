from django.shortcuts import render
from competition.models import Competition

# Create your views here.
def CompetitionList(request):
    list = Competition.objects.all()
    context = {}
    context['list'] = list
    return render(request,"../templates/CompetitionList.html", context)
