from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        # 디폴트 정렬
        # 쿼리셋에서 order_by를 지정하지 않으면, 적용
        ordering = ["-pk"]
