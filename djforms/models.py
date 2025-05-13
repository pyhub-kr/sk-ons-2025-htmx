from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .form_template_fields import get_field_type, get_field_type_choices
from .fields.multiselectfield import MultiSelectField


class FormTemplate(models.Model):
    title = models.CharField(max_length=500, verbose_name="제목")
    description = models.TextField(blank=True, verbose_name="설명")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="만료일")
    allow_anonymous = models.BooleanField(default=False, verbose_name="익명 제출 허용")
    is_active = models.BooleanField(default=True, verbose_name="활성화")

    class Meta:
        verbose_name = "폼"
        verbose_name_plural = "폼 목록"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class FormTemplateField(models.Model):
    class FileTypes(models.TextChoices):
        PDF = "pdf", "PDF"
        JPG = "jpg", "JPG"
        PNG = "png", "PNG"
        GIF = "gif", "GIF"
        TXT = "txt", "TXT"
        CSV = "csv", "CSV"
        XLSX = "xlsx", "XLSX"
        DOCX = "docx", "DOCX"
        PPTX = "pptx", "PPTX"
        ALL_FILES = "all", "All Files"

    FIELD_TYPE_CHOICES = get_field_type_choices()
    assert len(FIELD_TYPE_CHOICES) > 0

    uuid = models.UUIDField(editable=False, default=uuid4)
    field_type = models.CharField(
        max_length=50,
        choices=FIELD_TYPE_CHOICES,
        default=FIELD_TYPE_CHOICES[0][0],
        verbose_name="필드 타입",
    )
    form_template = models.ForeignKey(
        FormTemplate,
        on_delete=models.CASCADE,
        related_name="field_set",
        verbose_name="폼",
    )
    question = models.CharField(max_length=1000, blank=True, verbose_name="질문")
    description = models.TextField(blank=True, verbose_name="설명")
    required = models.BooleanField(default=False, verbose_name="필수")
    choices = models.TextField(blank=True, verbose_name="선택지")
    file_types = MultiSelectField(
        choices=FileTypes.choices,  # noqa
        max_length=10,
        blank=True,
        null=True,
        verbose_name="허용 파일 형식",
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name="순서")

    class Meta:
        verbose_name = "폼 필드"
        verbose_name_plural = "폼 필드 목록"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.form_template.title} - {self.question}"

    def clean(self):
        field_type = get_field_type(self.field_type)
        if not field_type:
            raise ValidationError({"field_type": "유효하지 않은 필드 타입입니다."})

        # TODO: choices 포맷에 대한 유효성 검사 추가
        if field_type.has_choices and not self.choices:
            raise ValidationError({"choices": "선택지를 입력해주세요."})

        if field_type.has_file_types and not self.file_types:
            raise ValidationError({"file_types": "허용할 파일 형식을 입력해주세요."})

    def get_delete_url(self) -> str:
        return reverse(
            "djforms:form_template_field_delete", args=[self.form_template.pk, self.pk]
        )


class FormResponse(models.Model):
    form_template = models.ForeignKey(
        FormTemplate,
        on_delete=models.CASCADE,
        related_name="response_set",
        verbose_name="폼",
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="제출일")
    ip_address = models.GenericIPAddressField(verbose_name="IP 주소")
    user_agent = models.TextField(verbose_name="User Agent")

    class Meta:
        verbose_name = "폼 응답"
        verbose_name_plural = "폼 응답 목록"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.form_template.title} - {self.submitted_at}"


class FormResponseField(models.Model):
    form_template_field = models.ForeignKey(
        FormTemplateField,
        on_delete=models.CASCADE,
        related_name="response_set",
        verbose_name="필드",
    )
    form_response = models.ForeignKey(
        FormResponse,
        on_delete=models.CASCADE,
        related_name="field_set",
        verbose_name="응답",
    )
    value = models.TextField(verbose_name="값")
    file = models.FileField(
        upload_to="form_responses/", null=True, blank=True, verbose_name="파일"
    )

    class Meta:
        verbose_name = "응답 필드"
        verbose_name_plural = "응답 필드 목록"

    def __str__(self):
        return f"{self.form_template_field.question} - {self.value}"
