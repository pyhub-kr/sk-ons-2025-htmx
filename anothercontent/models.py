from django.db import models
from django.urls import reverse

# Create your models here.
class Content(models.Model):
    CONTENT_TYPES = [
        ('post', '게시글'),
        ('survey', '설문조사'),
        ('exam', '시험'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('content_detail', kwargs={'pk': self.pk})


class Media(models.Model):
    MEDIA_TYPES = [
        ('text', '텍스트'),
        ('image', '이미지'),
        ('file', '파일'),
    ]
    content = models.ForeignKey(Content, related_name='media_items', on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    text_content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_media_type_display()} for {self.content.title}"


class Question(models.Model):
    QUESTION_TYPES = [
        ('mc', '객관식'),
        ('short', '단답형'),
        ('essay', '서술형'),
        ('rating', '별점'),
    ]
    content = models.ForeignKey(Content, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.choice_text