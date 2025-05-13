from typing import Any, Optional

from django import forms
from django.http import HttpRequest
from django.template.loader import render_to_string

from .models import FormTemplate, FormTemplateField, FormResponse, FormResponseField
from .form_template_fields import get_field_type


class FormTemplateForm(forms.ModelForm):
    class Meta:
        model = FormTemplate
        fields = [
            "title",
            "description",
            "allow_anonymous",
            "is_active",
            "expires_at",
        ]


class FormTemplateFieldForm(forms.ModelForm):
    DEFAULT_TEMPLATE_NAME = "djforms/fields/not_found.html"

    class Meta:
        model = FormTemplateField
        fields = [
            "question",
            "description",
            "required",
            "choices",
            "file_types",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "choices": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        instance: Optional[FormTemplateField] = kwargs.pop("instance", None)
        if instance is not None:
            prefix = f"field_{instance.uuid.hex}"
            self.field_type = get_field_type(instance.field_type)
        else:
            prefix = None
            self.field_type = None

        super().__init__(*args, instance=instance, prefix=prefix, **kwargs)

    def render_template(
        self,
        request: HttpRequest,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        if self.field_type is None:
            template_name = self.DEFAULT_TEMPLATE_NAME
        else:
            template_name = self.field_type.template_name or self.DEFAULT_TEMPLATE_NAME

        return render_to_string(
            template_name=template_name,
            context=dict(
                form=self,
                field_type=self.field_type,
                form_template_field=self.instance,
                **(context or {}),
            ),
            request=request,
        )

    def clean(self):
        cleaned_data = super().clean()

        print("BEFORE cleaned_data :", repr(cleaned_data))

        if self.field_type is not None:
            # 선택지 검증
            if self.field_type.has_choices:
                choices = cleaned_data.get("choices")
                print("choices :", repr(choices))
                # if not choices:
                #     raise forms.ValidationError({"choices": "선택지를 입력해주세요."})
                # if len(choices.split(",")) < 2:
                #     raise forms.ValidationError(
                #         {"choices": "선택지는 2개 이상이어야 합니다."}
                #     )

            # 파일 타입 검증
            if self.field_type.has_file_types:
                file_types = cleaned_data.get("file_types")
                if not file_types:
                    raise forms.ValidationError(
                        {"file_types": "허용할 파일 형식을 입력해주세요."}
                    )

        print("AFTER cleaned_data :", repr(cleaned_data))

        return cleaned_data


class FormResponseForm(forms.ModelForm):
    class Meta:
        model = FormResponse
        fields = []

    def __init__(self, form_template: FormTemplate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_template = form_template

        for form_template_field in form_template.field_set.all():
            field_type = get_field_type(form_template_field.field_type)
            if not field_type:
                continue

            # TODO: question/description을 form Field에 적절히 적용하기
            form_field = field_type.get_form_field(
                label=form_template_field.question,
                required=form_template_field.required,
                help_text=form_template_field.description,
                choices=(
                    [
                        (c.strip(), c.strip())
                        for c in form_template_field.choices.split(",")
                    ]
                    if field_type.has_choices and form_template_field.choices
                    else None
                ),
            )

            self.fields[form_template_field.name] = form_field
