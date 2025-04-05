from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from .models import Content, Media, Question, Choice
from .forms import ContentForm, MediaForm, QuestionForm, ChoiceForm, MediaFormSet, QuestionFormSet, ChoiceFormSet


class ContentCreateView(CreateView):
    model = Content
    form_class = ContentForm
    template_name = 'anothercontent/content/content_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['media_formset'] = MediaFormSet(self.request.POST, self.request.FILES)
            context['question_formset'] = QuestionFormSet(self.request.POST)
        else:
            context['media_formset'] = MediaFormSet()
            context['question_formset'] = QuestionFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        media_formset = context['media_formset']
        question_formset = context['question_formset']

        if media_formset.is_valid() and question_formset.is_valid():
            self.object = form.save()

            media_formset.instance = self.object
            media_formset.save()

            question_formset.instance = self.object
            question_instances = question_formset.save()

            # 각 질문에 대한 선택지 처리 (객관식인 경우)
            for question in question_instances:
                if question.question_type == 'mc':
                    # HTMX를 통해 나중에 처리
                    pass

            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


# HTMX용 뷰 함수
def add_media_form(request):
    """HTMX를 통해 동적으로 미디어 폼 추가"""
    form_idx = request.GET.get('form_idx')
    form = MediaForm(prefix=f'media_items-{form_idx}')
    return render(request, 'anothercontent/content/partials/media_form.html', {'form': form, 'form_idx': form_idx})


def add_question_form(request):
    """HTMX를 통해 동적으로 질문 폼 추가"""
    form_idx = request.GET.get('form_idx')
    form = QuestionForm(prefix=f'questions-{form_idx}')
    return render(request, 'anothercontent/content/partials/question_form.html', {'form': form, 'form_idx': form_idx})


def add_choice_form(request, question_id=None):
    """HTMX를 통해 동적으로 선택지 폼 추가"""
    form_idx = request.GET.get('form_idx')
    question_idx = request.GET.get('question_idx')

    if question_id:
        question = get_object_or_404(Question, id=question_id)
        form = ChoiceForm(prefix=f'question-{question_id}-choice-{form_idx}')
    else:
        form = ChoiceForm(prefix=f'questions-{question_idx}-choices-{form_idx}')

    return render(request, 'anothercontent/content/partials/choice_form.html', {'form': form, 'form_idx': form_idx})


def toggle_media_fields(request):
    """HTMX를 통해 미디어 타입에 따라 필드 표시 전환"""
    media_type = request.GET.get('media_type')
    form_idx = request.GET.get('form_idx')

    return render(request, 'anothercontent/content/partials/media_fields.html', {
        'media_type': media_type,
        'form_idx': form_idx
    })


def toggle_question_fields(request):
    """HTMX를 통해 질문 타입에 따라 필드 표시 전환"""
    question_type = request.GET.get('question_type')
    form_idx = request.GET.get('form_idx')

    return render(request, 'anothercontent/content/partials/question_fields.html', {
        'question_type': question_type,
        'form_idx': form_idx
    })