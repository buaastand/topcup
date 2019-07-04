from django.db import models
from techworks.models import WorkInfo
from users.models import Expert


# Create your models here.
class Review(models.Model):
    REVIEW_STATUS = (
        (0,'邮件已发出'),
        (1,'专家已拒绝'),
        (2,'专家尚未评价'),
        (3,'评价已暂存'),
        (4,'评价已提交'),
        # (0, "未接受"),
        # (1, "已接收"),
        # (2, "已评价"),
    )
    work = models.ForeignKey(WorkInfo, on_delete=models.CASCADE, verbose_name="作品")
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, verbose_name="专家")
    score = models.FloatField(verbose_name="评分")
    comment = models.TextField(verbose_name="评审意见")
    add_time = models.DateField(verbose_name="邀请时间")
    review_status = models.IntegerField(choices=REVIEW_STATUS, verbose_name="评价状态")

    class Meta:
        verbose_name = "评价"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.work) + ":" + str(self.expert)
