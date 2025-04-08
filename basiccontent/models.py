from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ItemBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Text(ItemBase):
    text = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to="files")


class Image(ItemBase):
    image = models.ImageField(upload_to="images")


class Content(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("text", "file", "image")},
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")

    def delete(self, *args, **kwargs):
        # Delete the generic related item first
        if self.item:
            self.item.delete()
        super().delete(*args, **kwargs)


class PostType(models.Model):
    post_type = models.CharField(max_length=30, verbose_name="글 유형")

class MainPost(models.Model):
    """메인 글을 정의하는 모델"""
    title = models.CharField(max_length=255, verbose_name="대주제")
    post_type = models.ForeignKey(PostType, on_delete=models.CASCADE, verbose_name="글 유형")
    description = models.TextField(null=True, blank=True, verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MainPost {self.title}_{self.post_type.post_type}"


class SubPost(models.Model):
    """메인 글에 들어갈 내용"""
    main_post = models.ForeignKey(MainPost, on_delete=models.CASCADE, related_name="sub_posts")
    title = models.CharField(max_length=255, verbose_name="서브 제목")
    description = models.TextField(null=True, blank=True, verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MainPost {self.main_post.title} {self.main_post.post_type.post_type}_SubPost {self.title}"


class PostContent(models.Model):
    """글에 넣을 컨텐츠"""
    post = models.ForeignKey(SubPost, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1, verbose_name="컨텐츠 순서")


class PostOptions(models.Model):
    """ 메인글에 필요한 서브필드, 객관식인 경우 보기들, 서술형인 경우 """
    post = models.ManyToManyField(SubPost)
    option_order = models.PositiveIntegerField(default=1, verbose_name="서브필드 순서")
    description = models.TextField(null=True, blank=True, verbose_name="서브필드 내용")
