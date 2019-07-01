from django.shortcuts import render
from django.views.generic.base import View
from techworks.models import WorkInfo
from .models import Review
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
class ExpertReviewView():
    def list(request):
        return render(request, 'work-list.html')

    @csrf_exempt
    def show(request):
        work_id = request.GET.get('work_id')
        expert_id = request.GET.get('expert_id')
        try:
            review = Review.objects.get(work_id=work_id, expert_id=expert_id)
            if review.review_status == 0:  # 还没评过
                return render(request, 'judgeWork.html', {'status': 0, 'expert_id':expert_id, 'work_id':work_id})
            else:  # 暂存或评价过
                return render(request, 'judgeWork.html', {'status': review.review_status, 'score': review.score, 'comment': review.comment, 'expert_id':expert_id, 'work_id':work_id})
        except:
            Review.objects.create(work_id=work_id, expert_id=expert_id, score=0, comment='', review_status=0, add_time='2019-07-02')
            return render(request, 'judgeWork.html', {'status': 0, 'expert_id':expert_id, 'work_id':work_id})

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
                review = Review.objects.get(expert_id=expert_id, work_id=work_id)
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
