from typing import Optional, Type, Any
from django import forms


class FormTemplateFieldType:
    """폼 필드 타입의 기본 클래스"""

    def __init__(
        self,
        type: str,
        label: str,
        form_field_class: Type[forms.Field],
        has_choices: bool = False,
        has_file_types: bool = False,
        template_name: Optional[str] = None,
        icon: Optional[str] = None,
    ):
        self.type = type
        self.label = label
        self.form_field_class = form_field_class
        self.has_choices = has_choices
        self.has_file_types = has_file_types
        self.template_name = template_name
        self.icon = icon

    def get_form_field(self, **kwargs) -> forms.Field:
        """Django Form Field 인스턴스를 반환"""
        return self.form_field_class(**kwargs)


# 기본 필드 타입 정의
FORM_TEMPLATE_FIELD_TYPES: dict[str, FormTemplateFieldType] = {
    "text": FormTemplateFieldType(
        type="text",
        label="단답형",
        form_field_class=forms.CharField,
        icon="bi bi-input-cursor-text",
        template_name="djforms/fields/text.html",
    ),
    "textarea": FormTemplateFieldType(
        type="textarea",
        label="장문형",
        form_field_class=forms.CharField,
        icon="bi bi-card-text",
        template_name="djforms/fields/textarea.html",
    ),
    "radio": FormTemplateFieldType(
        type="radio",
        label="객관식 질문",
        form_field_class=forms.ChoiceField,
        has_choices=True,
        icon="bi bi-ui-radios",
        template_name="djforms/fields/radio.html",
    ),
    "checkbox": FormTemplateFieldType(
        type="checkbox",
        label="체크박스",
        form_field_class=forms.MultipleChoiceField,
        has_choices=True,
        icon="bi bi-ui-checks",
        template_name="djforms/fields/checkbox.html",
    ),
    "select": FormTemplateFieldType(
        type="select",
        label="드롭다운",
        form_field_class=forms.ChoiceField,
        has_choices=True,
        icon="bi bi-caret-down-square",
        template_name="djforms/fields/select.html",
    ),
    "file": FormTemplateFieldType(
        type="file",
        label="파일 업로드",
        form_field_class=forms.FileField,
        has_file_types=True,
        icon="bi bi-upload",
        # template_name="djforms/fields/file.html",
    ),
}


def get_field_type(name: str) -> Optional[FormTemplateFieldType]:
    """필드 타입 이름으로 FieldType 인스턴스를 반환"""
    return FORM_TEMPLATE_FIELD_TYPES.get(name)


def get_field_type_choices() -> list[tuple[Any, Any]]:
    """폼에서 사용할 필드 타입 선택지 반환"""
    return [
        (name, field_type.label)
        for name, field_type in FORM_TEMPLATE_FIELD_TYPES.items()
    ]
