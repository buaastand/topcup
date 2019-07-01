from django.shortcuts import render,HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import WorkInfo
from django.db.models import Q
from competition.models import CompetitionRegistration,Competition
from users.models import Student

# Create your views here.
def test(request):
    request.user.username
# @login_required(login_url='/login/')
# @method_decorator(login_required,name='dispatch')
class TechWorkListView(View):
    # @login_required(login_url='/login/')
    def get(self, request):
        # if request.GET.get('workid', None) is None:
        #     WorkInfo.objects.create()
        username = request.user.username
        registrationlist = CompetitionRegistration.objects.filter(Q(first_auth__user__username=username)
                                                                 | Q(second_auth__user__username=username)
                                                                 | Q(third_auth__user__username=username)
                                                                 | Q(forth_auth__user__username=username)
                                                                 | Q(fifth_auth__user__username=username)
                                                                 )
        worklist_origin = WorkInfo.objects.filter(registration__in=registrationlist)
        # work = WorkInfo.objects.get(work_id='1').wo
        WORKTYPE_MAP={
            1: "科技发明制作",
            2: "调查报告和学术论文"
        }
        FIELD_MAP={
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
        }
        worklist_ret = []
        for work in worklist_origin:
            worklist_ret.append({
                'work_id': work.work_id,
                'first_author': work.registration.first_auth,
                'title': work.title,
                'work_type': WORKTYPE_MAP[work.work_type],
                'field': FIELD_MAP[work.field],
                'competition': work.registration.competition,
                'submitted': work.submitted,
            })
        return render(request, 'techwork_list.html', {'worklist':worklist_ret})


class TechWorkView(View):
    def get(self, request):
        work_id = request.GET.get('workid', None)
        comptition_id = request.GET.get('cptid', None)
        username = request.user.username
        if username=="":
            username = "16211086"
        work = None
        company_ret = []
        if work_id is None:
            if comptition_id is not None:
                registration = CompetitionRegistration.objects.create(first_auth=Student.objects.get(user__username=username),competition=Competition.objects.get(id=comptition_id))
                registration.save()
                work_cnt = WorkInfo.objects.count()
                BASE_NUM = 10000
                work = WorkInfo.objects.create(registration=registration,title="",detail="",innovation="",keywords="",avg_score=0,work_id=BASE_NUM+work_cnt,work_type=1,field=1)
                work.save()
            else:
                return HttpResponse(status=400)
        else:
            work = WorkInfo.objects.get(work_id=work_id)
            registration = work.registration
            company = []
            if registration.second_auth is not None:
                auth = registration.second_auth

                company.append(registration.second_auth)
            if registration.third_auth is not None:
                company.append(registration.third_auth)
            if registration.forth_auth is not None:
                company.append(registration.forth_auth)
            if registration.fifth_auth is not None:
                company.append(registration.fifth_auth)
            company_ret=[]
            for auth in company:
                company_ret.append({"stu_id":auth.stu_id,
                                    "name": auth.name,
                                    "degree": auth.degree,
                                    "phone": auth.phone,
                                    "email":auth.user.email})
        return render(request, 'submit_techwork.html', {'work':work,'company':company_ret})

    def post(self, request):

