from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import WorkInfo, Appendix
from django.db.models import Q
from competition.models import CompetitionRegistration, Competition
from users.models import Student
from django.db import transaction
from competition.views import GetUserIdentitiy
import datetime
import json


# Create your views here.
@csrf_exempt
def work_info(request):
    DEGREE = ['大专','大学本科','硕士研究生','博士研究生']
    user_name, user_identity = GetUserIdentitiy(request)
    information = {}
    workInfo = WorkInfo.objects.get(id=request.GET['work_id'])
    workAppendix = Appendix.objects.filter(work_id=request.GET['work_id'])
    workAuthor = CompetitionRegistration.objects.get(id=request.GET['work_id'])
    workFirstAuthorInfo = Student.objects.get(user_id=workAuthor.first_auth_id)
    authorList = []

    if(workAuthor.second_auth_id):
        workSecondAuthorInfo = Student.objects.get(user_id=workAuthor.second_auth_id)
        authorList.append({'name': workSecondAuthorInfo.name,
                           'stu_id': workSecondAuthorInfo.stu_id,
                           'degree': DEGREE[workSecondAuthorInfo.degree],
                           'phone': workSecondAuthorInfo.phone,
                           'email': workSecondAuthorInfo.user.email})
    else:
        workSecondAuthorInfo = ''

    if (workAuthor.third_auth_id):
        workThirdAuthorInfo = Student.objects.get(user_id=workAuthor.third_auth_id)
        authorList.append({'name': workThirdAuthorInfo.name,
                           'stu_id': workThirdAuthorInfo.stu_id,
                           'degree': DEGREE[workThirdAuthorInfo.degree],
                           'phone': workThirdAuthorInfo.phone,
                           'email': workThirdAuthorInfo.user.email})
    else:
        workThirdAuthorInfo = ''

    if (workAuthor.forth_auth_id):
        workForthAuthorInfo = Student.objects.get(user_id=workAuthor.forth_auth_id)
        authorList.append({'name': workForthAuthorInfo.name,
                           'stu_id': workForthAuthorInfo.stu_id,
                           'degree': DEGREE[workForthAuthorInfo.degree],
                           'phone': workForthAuthorInfo.phone,
                           'email': workForthAuthorInfo.user.email})
    else:
        workFourthAuthorInfo = ''

    if (workAuthor.fifth_auth_id):
        workFifthAuthorInfo = Student.objects.get(user_id=workAuthor.fifth_auth_id)
        authorList.append({'name': workFifthAuthorInfo.name,
                           'stu_id': workFifthAuthorInfo.stu_id,
                           'degree': DEGREE[workFifthAuthorInfo.degree],
                           'phone': workFifthAuthorInfo.phone,
                           'email': workFifthAuthorInfo.user.email})
    else:
        workFifthAuthorInfo = ''

    information = {'workInfo': workInfo}
    information['workAppendix']= workAppendix
    information['workAuthor'] = workAuthor
    information['authorList'] = authorList
    information['username'] = user_name
    information['useridentity'] = user_identity

    return render(request, '../templates/viewWorkInfo.html', information)

def searchstu(request):
    DEGREE_MAP = {
            1: "大专",
            2: "大学本科",
            3: "硕士研究生",
            4: "博士研究生",
    }
    stuid = request.GET.get('stu_id')
    student = Student.objects.get(stu_id=stuid)
    ret = {"student":{
                    "stu_id":student.stu_id,
                    "name":student.name,
                    "degree":DEGREE_MAP[student.degree],
                    "phone":student.phone,
                    "email":student.user.email
                    }}
    return JsonResponse(ret)


# @login_required(login_url='/login/')
# @method_decorator(login_required,name='dispatch')
class TechWorkListView(View):
    # @login_required(login_url='/login/')
    def get(self, request):
        # if request.GET.get('workid', None) is None:
        #     WorkInfo.objects.create()
        username = request.user.username
        if username == "":
            username = "16211086"
        registrationlist = CompetitionRegistration.objects.filter(Q(first_auth__user__username=username)
                                                                  | Q(second_auth__user__username=username)
                                                                  | Q(third_auth__user__username=username)
                                                                  | Q(forth_auth__user__username=username)
                                                                  | Q(fifth_auth__user__username=username)
                                                                  )
        worklist_origin = WorkInfo.objects.filter(registration__in=registrationlist)
        # work = WorkInfo.objects.get(work_id='1').wo
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
        worklist_ret = []
        for work in worklist_origin:
            worklist_ret.append({
                'work_id': work.work_id,
                'first_author': work.registration.first_auth.name,
                'title': work.title,
                'work_type': WORKTYPE_MAP[work.work_type],
                'field': FIELD_MAP[work.field],
                'competition': work.registration.competition.title,
                'submitted': "已提交" if work.submitted else "暂存",
            })

        user_name, user_identity = GetUserIdentitiy(request)
        return render(request, 'techwork_list.html', {'worklist': worklist_ret,'useridentity':user_identity})


class TechWorkView(View):
    def get(self, request):
        work_id = request.GET.get('workid', None)
        comptition_id = request.GET.get('cptid', None)
        username = request.user.username
        if username == "":
            username = "16211086"
        work = None
        company_ret = []
        file_docu = []
        file_photo = []
        file_video = []
        if work_id is None:
            if comptition_id is not None:
                registration = CompetitionRegistration.objects.create(
                    first_auth=Student.objects.get(user__username=username),
                    competition=Competition.objects.get(id=comptition_id))
                registration.save()
                work_cnt = WorkInfo.objects.count()
                BASE_NUM = 10000
                work = WorkInfo.objects.create(registration=registration, title="", detail="", innovation="",
                                               keywords="", avg_score=0, work_id=BASE_NUM + work_cnt, work_type=1,
                                               field=1)
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
            company_ret = []
            for auth in company:
                company_ret.append({"stu_id": auth.stu_id,
                                    "name": auth.name,
                                    "degree": auth.degree,
                                    "phone": auth.phone,
                                    "email": auth.user.email})

            filelist = Appendix.objects.filter(work__work_id=work.work_id)

            for file in filelist:
                if(file.appendix_type == 0):
                    file_docu.append({"name": file.filename,"url": file.file.name})
                if(file.appendix_type == 1):
                    file_photo.append({"name": file.filename, "url": file.file.name})
                if (file.appendix_type == 2):
                    file_video.append({"name": file.filename, "url": file.file.name})

        user_name, user_identity = GetUserIdentitiy(request)
        return render(request, 'submit_techwork.html', {'work': work, 'company': company_ret, 'docu': file_docu, 'photo': file_photo, 'video': file_video,'useridentity':user_identity})

    def post(self, request):
        try:
            with transaction.atomic():
                work_id = int(request.POST.get('work_id'))
                work = WorkInfo.objects.get(work_id=work_id)
                registration = work.registration
                AUTH_MAP = {
                    0: registration.second_auth,
                    1: registration.third_auth,
                    2: registration.forth_auth,
                    3: registration.fifth_auth
                }
                team = json.loads(request.POST.get("company_table",[]))
                for id in range(0,4):
                    if len(team) > id:
                        stu = team[id]
                    else:
                        stu = None
                    if id==0:
                        registration.second_auth = Student.objects.get(stu_id=stu["stu_id"]) if stu else None
                    if id==1:
                        registration.third_auth = Student.objects.get(stu_id=stu["stu_id"]) if stu else None
                    if id==2:
                        registration.forth_auth = Student.objects.get(stu_id=stu["stu_id"]) if stu else None
                    if id==3:
                        registration.fifth_auth = Student.objects.get(stu_id=stu["stu_id"]) if stu else None

                work.title = request.POST.get('title', work.title)
                work.detail = request.POST.get('detail', work.detail)
                work.innovation = request.POST.get('innovation', work.innovation)
                work.keywords = request.POST.get('keywords', work.keywords)
                work.work_type = int(request.POST.get('work_type', work.work_type))
                work.field = int(request.POST.get("field", work.field))
                work.submitted = True if int(request.POST.get("submitted", work.submitted)) == 1 else False
                FILE_TYLE_MAP = {
                    "document": 0,
                    "photo": 1,
                    "video": 2
                }
                if len(request.FILES) > 0:
                    for k, file in request.FILES.items():
                        # file = file[0]
                        filename = file._name
                        filedata = file
                        filetype = FILE_TYLE_MAP[file.field_name.split('_')[0]]
                        filedate = datetime.date.today()
                        Appendix.objects.create(filename=filename, appendix_type=filetype, upload_date=filedate,
                                                file=filedata, work=work)

                # team = json.loads(request.POST.get('company_table')) if request.POST.get(
                #     'company_table') != "" else None
                #
                # if team:
                #     for order, auth in enumerate(team):
                #         AUTH_MAP[order] = Student.objects.get(stu_id=auth['stu_id'])

                registration.save()
                work.save()
        except Exception as e:
            print(e)
            return HttpResponse(status=400)
        return HttpResponse(status=200)

        # file = request.FILES.get("file")
        # dataPOST = json.loads(request.body)
        # dataPOST['birthdate'] = dataPOST['birthdate'][0:10]
        # dataPOST['enroll_time'] = dataPOST['enroll_time'][0:10]
        # register_form = RegisterForm(dataPOST)
        # if register_form.is_valid():
        #     email = dataPOST.get('email', '')
        #     if Student.objects.filter(user__email=email):
        #         return render(request, "register.html", {"register_form": register_form, "msg": "该邮箱已注册"})
        #     password = dataPOST.get('password', '')
        #
        #     # 创建BaseUser对象
        #     baseuser = BaseUser()
        #     baseuser.username = dataPOST.get('stu_id', '')
        #     baseuser.password = make_password(password)
        #     baseuser.type = 1
        #     baseuser.email = email
        #     baseuser.save()
