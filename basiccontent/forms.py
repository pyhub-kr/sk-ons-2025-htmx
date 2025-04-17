from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

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
                'placeholder': '숫자만 입력하세요',
                'data-mask': '000-0000-0000'
            }),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_phone_number(self):
        """전화번호에 하이픈 자동 추가"""
        phone_number = self.cleaned_data.get('phone_number', '')
        # 숫자만 남기기
        digits = ''.join(filter(str.isdigit, phone_number))

        # 적절한 길이인지 확인
        if len(digits) != 11:
            raise forms.ValidationError("전화번호는 11자리 숫자여야 합니다.")

        # 하이픈 추가
        formatted_number = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        return formatted_number

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
    extra=3,  # 기본적으로 3개의 답변 입력 폼을 제공
    can_delete=False
)