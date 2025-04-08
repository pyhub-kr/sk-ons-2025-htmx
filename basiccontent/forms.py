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
class BasicPostForm(forms.ModelForm):
    class Meta:
        model = BasicPost
        fields = ['title', 'description', 'post_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'post_type': forms.Select(attrs={'class': 'form-control'}),
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
    parent_model=BasicPost,
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