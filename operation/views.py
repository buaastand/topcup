from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from competition.views import GetUserIdentitiy
from competition.models import Competition
from techworks.models import WorkInfo
from users.models import Expert
from .models import Review


# Create your views here.
def DownLoadPDF(request):
    pass




class ExpertReviewListView(View):
    def get(self, request):
        user_id = request.user.id
        review_invention_ret = []
        review_report_ret = []
        review_list = Review.objects.filter(expert__user_id=user_id)

        TAG_MAP = {
            1: "未评审",
            2: "已评审"
        }

        for review in review_list:
            work = WorkInfo.objects.get(id=review.work_id)
            if work.work_type == 1:
                review_invention_ret.append({
                    'id': review.id,
                    'tilte': work.title,
                    'keywords': work.keywords,
                    'score': review.score,
                    'tag': TAG_MAP[review.review_status]
                })
            else:
                review_report_ret.append({
                    'id': review.id,
                    'tilte': work.title,
                    'keywords': work.keywords,
                    'score': review.score,
                    'tag': TAG_MAP[review.review_status]
                })

        user_name, user_identity = GetUserIdentitiy(request)
        return render(request, 'ExpertReviewWorkList.html', {'invention': review_invention_ret,
                                                             'report': review_report_ret,
                                                             'username': user_name, 'useridentity': user_identity})

class ExpertReviewView(View):
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
