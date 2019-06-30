from django.shortcuts import render

# Create your views here.
def CompetitionDetail(request):
    return render(request,"../templates/CompetitionDetail.html")

def CompetitionInit(request):
    return render(request, "../templates/CompetitionInit.html")

