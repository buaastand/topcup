from django.shortcuts import render
from django.views import View
from .models import WorkInfo
# Create your views here.

class TechWorkListView(View):
    def get(self,request):
        # if request.GET.get('workid', None) is None:
        #     WorkInfo.objects.create()

        return render(request,'techwork_list.html',{})


class TechWorkView(View):
    def get(self,request):
        # if request.GET.get('workid',None) is None:
        #     WorkInfo.objects.create()


        return render(request,'submit_techwork.html',{})

    def post(self,request):
        pass