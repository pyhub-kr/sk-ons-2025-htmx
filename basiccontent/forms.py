import re

from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.core.exceptions import ValidationError

from basiccontent.models import *
from django.forms import BaseModelFormSet, HiddenInput, modelformset_factory, inlineformset_factory


class CustomBaseModelFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if self.can_delete:
            form.fields['DELETE'] = forms.BooleanField(
                required=False,
                initial=False,
                widget=HiddenInput()
            )

# 메인 글의 폼
class MainPostForm(forms.ModelForm):
    class Meta:
        model = MainPost
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class SubPostForm(forms.ModelForm):
    class Meta:
        model = SubPost
        fields = ['main_post', 'post_type', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


## 컨텐츠 타입 폼
class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ['text']

TextFormSet = modelformset_factory(Text, form=TextForm, extra=0, can_delete=True, formset=CustomBaseModelFormSet)

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=0, can_delete=True, formset=CustomBaseModelFormSet)

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

FileFormSet = modelformset_factory(File, form=FileForm, extra=0, can_delete=True, formset=CustomBaseModelFormSet)


class ContentTypeForm(forms.Form):
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(), initial=ContentType.objects.first())

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['content_type']

ContentFormSet = generic_inlineformset_factory(Content, form=ContentForm, extra=0, can_delete=True, formset=CustomBaseModelFormSet)

# Post - Content 연결 폼
class PostContentForm(forms.ModelForm):
    class Meta:
        model = PostContent
        fields = ['post', 'content', 'order']


PostContentFormSet = inlineformset_factory(
    parent_model=SubPost,
    model=PostContent,
    form=PostContentForm,
    fk_name='post',
    extra=0,
    can_delete=True,
)

PostContentTypeFormSet = inlineformset_factory(
    parent_model=Content,
    model=PostContent,
    form=PostContentForm,
    fk_name='content',
    extra=0,
    can_delete=True,
)


# 서브필드 폼
class PostOptionsForm(forms.ModelForm):
    class Meta:
        model = PostOptions
        fields = ['post', 'option_order', 'description']


class UserProfileForm(forms.ModelForm):
    """사용자 정보 입력 폼"""

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'birthday', 'gender']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control phone-number-input',
                'placeholder': '000-0000-0000',
                'data-mask': '000-0000-0000'
            }),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\d{3}-\d{4}-\d{4}$', phone_number):
            raise forms.ValidationError('전화번호는 000-0000-0000 형식이어야 합니다.')
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        phone_number = cleaned_data.get('phone_number')

        if username and phone_number:
            if User.objects.filter(username=username, phone_number=phone_number).exists():
                raise ValidationError("이미 설문에 응답하셨습니다.")
        return cleaned_data


class UserAnswerForm(forms.ModelForm):
    """사용자 답변 폼"""

    class Meta:
        model = UserAnswer
        fields = ['answer', 'subjective_answer']
        widgets = {
            'answer': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'subjective_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', None)
        super(UserAnswerForm, self).__init__(*args, **kwargs)

        if self.post:
            # 해당 SubPost와 연결된 PostOptions 가져오기
            post_options = PostOptions.objects.filter(post=self.post).order_by('option_order')
            self.fields['answer'].queryset = post_options

            # post_type에 따라 폼 필드 조정
            post_type = self.post.post_type.post_type

            # 객관식인 경우, 주관식 필드 숨기기
            if post_type == '객관식':
                self.fields['subjective_answer'].widget = forms.HiddenInput()

            # 주관식인 경우, 객관식 필드 숨기기
            elif post_type == '주관식':
                self.fields['answer'].widget = forms.HiddenInput()



class MultiSubjectiveAnswerForm(forms.ModelForm):
    """다중 주관식 답변 폼"""

    class Meta:
        model = MultiSubjectiveAnswers
        fields = ['answer_description']
        widgets = {
            'answer_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
        }


# 다중 주관식 답변을 위한 폼셋
MultiSubjectiveAnswerFormSet = forms.inlineformset_factory(
    UserAnswer,
    MultiSubjectiveAnswers,
    form=MultiSubjectiveAnswerForm,
    extra=0,
    can_delete=False
)