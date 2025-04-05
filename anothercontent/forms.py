from django import forms
from django.forms import inlineformset_factory
from .models import Content, Media, Question, Choice

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'content_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['media_type', 'text_content', 'file', 'image']
        widgets = {
            'text_content': forms.Textarea(attrs={'rows': 3, 'class': 'text-field hidden'}),
            'file': forms.FileInput(attrs={'class': 'file-field hidden'}),
            'image': forms.FileInput(attrs={'class': 'image-field hidden', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 초기 상태에서는 모든 필드를 숨김
        if self.instance.pk:
            if self.instance.media_type == 'text':
                self.fields['text_content'].widget.attrs.pop('hidden', None)
            elif self.instance.media_type == 'file':
                self.fields['file'].widget.attrs.pop('hidden', None)
            elif self.instance.media_type == 'image':
                self.fields['image'].widget.attrs.pop('hidden', None)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'required']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']

# 폼셋 정의
MediaFormSet = inlineformset_factory(
    Content, Media,
    form=MediaForm,
    extra=1,
    can_delete=True
)

QuestionFormSet = inlineformset_factory(
    Content, Question,
    form=QuestionForm,
    extra=1,
    can_delete=True
)

ChoiceFormSet = inlineformset_factory(
    Question, Choice,
    form=ChoiceForm,
    extra=3,
    can_delete=True
)