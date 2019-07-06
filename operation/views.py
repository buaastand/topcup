from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
import datetime
import json
from competition.views import GetUserIdentitiy
from techworks.models import WorkInfo
from users.models import Expert
from .models import Review

from django.db.models import Q


# Create your views here.
class ReviewWorkListView(View):
    # @login_required(login_url='/login/')
    def get(self, request):
        # if request.GET.get('workid', None) is None:
        #     WorkInfo.objects.create()
        worklist_origin = WorkInfo.objects.all()[:10]
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
        return render(request, 'reviewwork_list.html', {'worklist': worklist_ret,'useridentity':user_identity})

class ExpertReviewView():
    def list(request):
        return render(request, 'work-list.html')

    @csrf_exempt
    def show(request):
        user_name, user_identity = GetUserIdentitiy(request)
        work_id = request.GET.get('work_id')
        work = WorkInfo.objects.get(work_id=work_id)
        expert = Expert.objects.get(user__email=request.user.username)
        expert_id = expert.user.id
        # expert_id = request.GET.get('expert_id')
        try:
            review = Review.objects.filter(work=work, expert=expert)
            if len(review) > 0:
                review = review[0]
                if review.review_status == 0:  # 还没评过
                    return render(request, 'judgeWork.html',
                                  {'status': 0, 'score': 50, 'expert_id': expert_id, 'work_id': work_id,
                                   'useridentity': user_identity})
                else:  # 暂存或评价过
                    return render(request, 'judgeWork.html',
                                  {'status': review.review_status, 'score': review.score, 'comment': review.comment,
                                   'expert_id': expert_id, 'work_id': work_id, 'useridentity': user_identity})
            else:
                Review.objects.create(work=work, expert=expert, score=50, comment='', review_status=0,
                                      add_time='2019-07-02')
                return render(request, 'judgeWork.html',
                              {'status': 50, 'score': 0, 'expert_id': expert_id, 'work_id': work_id,
                               'useridentity': user_identity})
        except Exception as e:
            print(e)
            pass
    @csrf_exempt
    def judge(request):
        if request.method == 'POST':
            try:
                expert_id = request.POST.get('expert_id')
                print(expert_id)
                work_id = request.POST.get('work_id')
                score = request.POST.get('score')
                comment = request.POST.get('comment')
                status = request.POST.get('status')
                expert = Expert.objects.get(user__email=request.user.username)
                work = WorkInfo.objects.get(work_id=work_id)
                review = Review.objects.get(expert=expert, work=work)
                review.score = score
                review.comment = comment
                review.review_status = status
                review.save()
            except:
                print('评价失败')
        return render(request, 'judgeWork.html')


    def get(request):
        work_id = request.GET.get('work_id')
        expert_id = request.GET.get('expert_id')
        print(work_id, expert_id)
        try:
            review = Review.objects.get(work_id=work_id, expert_id=expert_id)
            if review.review_status == 0: #还没评过
                return JsonResponse({'status':0}, safe=False)
                # return render(request, 'judgeWork.html', {'status': 0})
            else: #暂存或评价过
                return JsonResponse({'status':review.review_status, 'score':review.score, 'comment':review.comment}, safe=False)
        except:
            Review.objects.create(work_id=work_id, expert_id=expert_id, score=0, comment='', review_status=0, add_time='2019-07-02')
            return JsonResponse({'status': 0}, safe=False)

class AssignWorkListView(View):
    """
    展示待分配作品列表
    """
    def get(self,request):
        cpt_id = request.GET.get('cpt_id','')
        worklist_origin = WorkInfo.objects.all().exclude(work_id__in=
            Review.objects.all().values_list('work_id', flat=True)) 
        # to do: 1.属于某个比赛的作品 2. 
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
                'work_id':work.work_id,
                'title':work.title,
                'work_type':WORKTYPE_MAP[work.work_type],
                'field':FIELD_MAP[work.field],
            })

        # 专家拒绝了待处理
        expertlist_origin = Expert.objects.all().exclude(user__id__in=
            Review.objects.filter(review_status__lt=4).values_list('expert__user__id', flat=True)) 
        expertlist_ret = []
        for expert in expertlist_origin:
            expertlist_ret.append({
                'expert_id':expert.user.id,
                'name':expert.name,
                'field':FIELD_MAP[expert.field],
                'email':expert.user.email,
            })

        user_name,user_identity = GetUserIdentitiy(request)
        return render(request,'assignwork_list.html',{'expertlist':expertlist_ret, 'worklist':worklist_ret , 'useridentity':user_identity,'username':user_name})

class AssignExpertView(View):
    """
    待分配专家
    """
    
    def get(self,request):
        pass

    def post(self,request):
        expert_list = request.POST.get('selected_expert')
        expert_list = json.loads(expert_list)
        work_list = request.POST.get('selected_work')
        work_list = json.loads(work_list)

        for expert_id in expert_list:
            for work_id in work_list:
                work_i = WorkInfo.objects.get(work_id=work_id) #数据库是否存在work_id相同的多个比赛
                expert_i = Expert.objects.get(user_id=expert_id)

                review = Review()
                review.work = work_i
                review.expert = expert_i
                review.add_time = datetime.date.today()
                review.score = -1
                review.review_status = 0 #邮件刚刚发出的状态
                review.save()
        cpt_name = WorkInfo.objects.get(work_id=work_list[0]).registration.competition.title


        # ref：https://www.cnblogs.com/lovealways/p/6701662.html
        import smtplib
        from email.mime.text import MIMEText
        sender = 'topcup2019@163.com'
        passwd = '123456zxcvbn'
        s = smtplib.SMTP_SSL('smtp.163.com', 465)
        s.login(sender, passwd)
        for expert_id in expert_list:
            receiver = Expert.objects.get(user_id=expert_id).user.email
            subject = '邀请参加'+'\"'+cpt_name+'\"'+'作品评审'
            content = '这是email内容'
            msg = MIMEText(content)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver
            try:
                s.sendmail(sender,receiver,msg.as_string())
            except:
                return JsonResponse({'Message':1})
                pass
        s.quit()
        return JsonResponse({'Message':0})

class ExptreviewListView(View):
    """
    展示已分配的专家-作品对
    """
    def get(self, request):

        FIELD_MAP = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
        }

        cpt_id = request.GET.get('cpt_id','')
        user_name,user_identity = GetUserIdentitiy(request)
        context = {}
        context['username'] = user_name
        context['useridentity'] = user_identity

        # 从Review表中选出该比赛的review
        reviews = Review.objects.all()
        review_ret = []
        for review_i in reviews:
            review_ret.append(
                {
                    'init_date': str(review_i.add_time),
                    'expert_id': review_i.expert.user.id,
                    'expert_name': review_i.expert.name,
                    'expert_field': review_i.expert.field,
                    'email': review_i.expert.user.email,
                    'work_id': review_i.work.work_id,
                    'work_name': review_i.work.title,
                    'work_type':review_i.work.work_type,
                    'work_field': review_i.work.field,
                    'review_state': review_i.review_status
                }
            )
        context['review_ret'] = review_ret

        #待选专家
        expertlist_origin = Expert.objects.all().exclude(user__id__in=
        Review.objects.all().values_list('expert__user__id', flat=True)) 
        expertlist_ret = []
        for expert in expertlist_origin:
            expertlist_ret.append({
                'expert_id':expert.user.id,
                'name':expert.name,
                'field':FIELD_MAP[expert.field],
                'email':expert.user.email,
            })
        context['expertlist'] = expertlist_ret

        return render(request, 'exptreview_list.html', context)

class ExptTreetableView(View):
    """
    以专家为主体展示已分配到某个专家的作品列表
    """
    def get(self, request):
        FIELD_MAP = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
        }

        cpt_id = request.GET.get('cpt_id','')
        user_name,user_identity = GetUserIdentitiy(request)
        context = {}
        context['username'] = user_name
        context['useridentity'] = user_identity

        # 从Review表中选出该比赛的review
        reviews = Review.objects.all()
        expt_tree_ret = {}

        # 以专家ID为key, value为专家信息和需要评审的作品列表
        for review_i in reviews:
            temp_expt_id = review_i.expert.user.id
            if temp_expt_id in expt_tree_ret.keys():
                expt_tree_ret[temp_expt_id]['works'].append(
                    {
                        'work_id': review_i.work.work_id,
                        'work_name': review_i.work.title,
                        'work_type':review_i.work.work_type,
                        'work_field': review_i.work.field,
                        'review_state': review_i.review_status,
                    }
                )
            else:
                expt_tree_ret[temp_expt_id] = {
                    'init_date': str(review_i.add_time),
                    'expert_id': review_i.expert.user.id,
                    'expert_name': review_i.expert.name,
                    'expert_field': review_i.expert.field,
                    'email': review_i.expert.user.email,
                    'expert_state': review_i.review_status,
                    'works':[]
                }
        
        #字典转换为列表
        expt_tree_ret = list(expt_tree_ret.values())
        context['expt_tree_ret'] = expt_tree_ret

        #待选专家
        expertlist_origin = Expert.objects.all().exclude(user__id__in=
            Review.objects.all().values_list('expert__user__id', flat=True)) 
        expertlist_ret = []
        for expert in expertlist_origin:
            expertlist_ret.append({
                'expert_id':expert.user.id,
                'expert_name':expert.name,
                'expert_field':FIELD_MAP[expert.field],
                'email':expert.user.email,
            })
        context['expertlist'] = expertlist_ret

        return render(request, 'expert_treetable.html', context)

class ReassignExpertView(View):
    """
    重新分配专家
    """
    
    def get(self,request):
        pass

    def post(self,request):
        originExpert_work = request.POST.get('originExpert_work')
        originExpert_expt = request.POST.get('originExpert_expt')
        originExpert_work = json.loads(originExpert_work)
        originExpert_expt = json.loads(originExpert_expt)

        # 为review更换专家
        for origin_expert_id in originExpert_expt.keys():
            # 用ID拿expert
            new_expert_id = originExpert_expt[origin_expert_id]
            new_expert = Expert.objects.filter(user__id=new_expert_id)
            origin_expert = Expert.objects.filter(user__id=origin_expert_id)

            try:
                for work_id in originExpert_work[origin_expert_id]:
                    review = Review.objects.filter(Q(expert=origin_expert) & Q(work__work_id=work_id))
                    review.expert = new_expert
                    review.review_status = 0
                    review.save()
            except:
                return JsonResponse({'Message':1})
                pass
                
        # ref：https://www.cnblogs.com/lovealways/p/6701662.html
        # import smtplib
        # from email.mime.text import MIMEText
        # sender = 'topcup2019@163.com'
        # passwd = '123456zxcvbn'
        # s = smtplib.SMTP_SSL('smtp.163.com', 465)
        # s.login(sender, passwd)
        # for expert_id in expert_list:
        #     receiver = Expert.objects.get(user_id=expert_id).user.email
        #     subject = '邀请参加'+'\"'+cpt_name+'\"'+'作品评审'
        #     content = '这是email内容'
        #     msg = MIMEText(content)
        #     msg['Subject'] = subject
        #     msg['From'] = sender
        #     msg['To'] = receiver
        #     try:
        #         s.sendmail(sender,receiver,msg.as_string())
        #     except:
        #         return JsonResponse({'Message':1})
        #         pass
        # s.quit()
        return JsonResponse({'Message':0})