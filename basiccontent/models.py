from django.core.validators import RegexValidator
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class User(models.Model):
    """유저 모델 : 회원이 아닌, 설문 응답 시 유저가 직접 작성한다."""
    username = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(
    max_length=20,
    unique=True,
    validators=[RegexValidator(
        regex=r'^\d{3}-\d{4}-\d{4}$',
        message="전화번호는 000-0000-0000 형식이어야 합니다.")])
    birthday = models.DateField()
    gender = models.CharField(max_length=10,
    choices=[('M', '남'), ('F', '여')],
    verbose_name="성별")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "유저"


class ItemBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Text(ItemBase):
    text = models.TextField()

    class Meta:
        verbose_name = "텍스트 컨텐츠"


class File(ItemBase):
    file = models.FileField(upload_to="files")

    class Meta:
        verbose_name = "파일 컨텐츠"


class Image(ItemBase):
    image = models.ImageField(upload_to="images")

    class Meta:
        verbose_name = "이미지 컨텐츠"



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

    class Meta:
        verbose_name = "컨텐츠 기록 모델"


class PostType(models.Model):
    post_type = models.CharField(max_length=30, verbose_name="글 유형")

    def __str__(self):
        return self.post_type

    class Meta:
        verbose_name = "글 유형"


class MainPost(models.Model):
    """메인 글을 정의하는 모델"""
    title = models.CharField(max_length=255, verbose_name="대주제")
    description = models.TextField(null=True, blank=True, verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MainPost {self.title}"

    class Meta:
        verbose_name = "메인 글"


class SubPost(models.Model):
    """메인 글에 들어갈 내용"""
    main_post = models.ForeignKey(MainPost, on_delete=models.CASCADE, related_name="sub_posts")
    post_type = models.ForeignKey(PostType, on_delete=models.CASCADE, verbose_name="글 유형")
    title = models.CharField(max_length=255, verbose_name="서브 제목")
    description = models.TextField(null=True, blank=True, verbose_name="내용")
    necessary = models.BooleanField(default=True, verbose_name="필수 여부")  # 필수 응답인지 표시
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MainPost {self.main_post.title} {self.post_type.post_type}_SubPost {self.title}"

    class Meta:
        verbose_name = "실제 문항"

class PostContent(models.Model):
    """글에 넣을 컨텐츠"""
    post = models.ForeignKey(SubPost, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1, verbose_name="컨텐츠 순서")

    class Meta:
        verbose_name = "글에 넣을 컨텐츠"


class PostOptions(models.Model):
    """ 메인글에 필요한 서브필드, 객관식인 경우 보기들, 온라인 시험인 경우 주관식 답안으로 활용"""
    post = models.ManyToManyField(SubPost)
    option_order = models.PositiveIntegerField(default=1, verbose_name="서브필드 순서")
    description = models.TextField(null=True, blank=True, verbose_name="서브필드 내용")

    class Meta:
        verbose_name = "객관식 보기"


class UserAnswer(models.Model):
    """유저가 작성한 답변"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(SubPost, on_delete=models.CASCADE)
    answer = models.ForeignKey(PostOptions, on_delete=models.CASCADE, verbose_name="답변", null=True, blank=True)
    subjective_answer = models.TextField(verbose_name="주관식 답변", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "유저 답안"


class MultiSubjectiveAnswers(models.Model):
    """다중답변 저장 모델"""
    user_answer = models.ForeignKey(UserAnswer, on_delete=models.CASCADE)
    answer_number = models.PositiveIntegerField(verbose_name="답안번호")
    answer_description = models.TextField(verbose_name="답안", null=True, blank=True)

    class Meta:
        verbose_name = "다중답안 저장용"


class AccessLog(models.Model):
    """유저가 설문에 접근한 기록"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)  # 로그인, 문제열람, 답안제출 등
    ip_address = models.GenericIPAddressField()

    class Meta:
        verbose_name = "유저 접근 기록"
