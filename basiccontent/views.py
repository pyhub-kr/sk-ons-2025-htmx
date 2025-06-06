from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from basiccontent.decorators import prevent_resubmission
from basiccontent.models import *
from basiccontent.forms import *
from django.contrib.contenttypes.models import ContentType
from django.views.generic import *


## MainPost CRUD Views
class MainPostListView(ListView):
    model = MainPost
    template_name = 'basiccontent/post_list.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_type'] = ContentType.objects.all()
        return context


class MainPostCreateView(CreateView):
    model = MainPost
    form_class = MainPostForm
    template_name = 'basiccontent/post_form.html'

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save()
        # success_url로 이동하는 HttpResponse 응답 생성
        # response = super().form_valid(form)

        if self.request.htmx:
        # if self.request.headers.get('HX-Request'):
            posts = MainPost.objects.all()
            return render(self.request, 'basiccontent/partials/post_list_partials.html', {'posts': posts})
        else:
            # TODO: success_url로 이동 응답
            return redirect(self.get_success_url())

    # def get_success_url(self):
    #     if self.request.headers.get('HX-Request'):
    #         return self.request.path
    #     return super().get_success_url()


class MainPostUpdateView(UpdateView):
    model = MainPost
    form_class = MainPostForm
    template_name = 'basiccontent/post_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            posts = MainPost.objects.all()
            return render(self.request, 'basiccontent/partials/post_list_partials.html', {'posts': posts})
        return response

    def get_success_url(self):
        if self.request.headers.get('HX-Request'):
            return self.request.path
        return super().get_success_url()


class MainPostDeleteView(DeleteView):
    model = MainPost

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if self.request.headers.get('HX-Request'):
            posts = MainPost.objects.all()
            return render(self.request, 'basiccontent/partials/post_list_partials.html', {'posts': posts})
        return super().delete(request, *args, **kwargs)



class MainPostDetailView(ListView):
    model = MainPost
    template_name = 'basiccontent/post_detail.html'
    context_object_name = 'posts'

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        posts = MainPost.objects.filter(id=post_id).prefetch_related(
            'sub_posts',
            'sub_posts__postcontent_set',
            'sub_posts__postcontent_set__content',
            'sub_posts__postoptions_set'
        )
        return posts

## SubPost CRUD Views
class SubPostListView(ListView):
    model = SubPost
    template_name = 'basiccontent/subpost/subpost_list.html'
    context_object_name = 'sub_posts'

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        sub_posts = SubPost.objects.filter(main_post_id=post_id).select_related('main_post')
        return sub_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs.get('post_id')
        return context


class SubPostCreateView(CreateView):
    model = SubPost
    form_class = SubPostForm
    template_name = 'basiccontent/subpost/subpost_form.html'
    context_object_name = 'sub_posts'

    def get_initial(self):
        initial = super().get_initial()
        post_id = self.kwargs.get('post_id')  # URL에서 post_id 가져오기
        if post_id:
            initial['main_post'] = post_id  # main_post 필드에 post_id 설정
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            sub_posts = SubPost.objects.filter(main_post_id=self.kwargs.get('post_id')).select_related('main_post', 'post_type')
            return render(self.request, 'basiccontent/subpost/subpost_list_partials.html', {'sub_posts': sub_posts})
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs.get('post_id')
        return context

    def get_success_url(self):
        if self.request.headers.get('HX-Request'):
            return self.request.path
        return super().get_success_url()

class SubPostUpdateView(UpdateView):
    model = SubPost
    form_class = SubPostForm
    template_name = 'basiccontent/subpost/subpost_form.html'
    context_object_name = 'sub_posts'

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            sub_posts = SubPost.objects.all()
            return render(self.request, 'basiccontent/subpost/subpost_list_partials.html', {'sub_posts': sub_posts})
        return response

    def get_success_url(self):
        if self.request.headers.get('HX-Request'):
            return self.request.path
        return super().get_success_url()


class SubPostDeleteView(DeleteView):
    model = SubPost

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if self.request.headers.get('HX-Request'):
            sub_posts = SubPost.objects.all()
            return render(self.request, 'basiccontent/subpost/subpost_list_partials.html', {'sub_posts': sub_posts})
        return super().delete(request, *args, **kwargs)



## Content CRUD Views
class PostContentUpdateView(UpdateView):
    model = SubPost
    template_name = 'basiccontent/post_content_form.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['formset'] = PostContentFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['formset'] = PostContentFormSet(instance=self.object)
            context['content_types'] = ContentType.objects.filter(
                model__in=('text', 'file', 'image')
            )
        return context


def get_content_form(request):
    """컨텐츠 타입에 따른 폼을 반환하는 뷰"""
    content_type_id = request.GET.get('content_type')
    post_id = request.GET.get('post')
    form_type = None

    if not content_type_id:
        return HttpResponse("Content type is required", status=400)

    content_type = ContentType.objects.get(id=content_type_id)

    if content_type.model == 'text':
        form = TextForm()
    elif content_type.model == 'file':
        form = FileForm()
    elif content_type.model == 'image':
        form = ImageForm()
    else:
        return HttpResponse("Invalid content type", status=400)

    return render(
        request,
        f'basiccontent/content_forms/{content_type.model}_form.html',
        {'form': form, 'content_type': content_type, 'post_id': post_id }
    )


@require_http_methods(["POST"])
def create_content(request):
    """새로운 컨텐츠 생성 뷰"""
    content_type_id = request.POST.get('content_type')
    if not content_type_id:
        return HttpResponse({"error": "Content type is required"}, status=400)

    content_type = ContentType.objects.get(id=content_type_id)

    # 컨텐츠 타입에 따른 폼 선택
    if content_type.model == 'text':
        form = TextForm(request.POST)
    elif content_type.model == 'file':
        form = FileForm(request.POST, request.FILES)
    elif content_type.model == 'image':
        form = ImageForm(request.POST, request.FILES)
    else:
        return HttpResponse({"error": "Invalid content type"}, status=400)

    if form.is_valid():
        # ItemBase를 상속받은 모델의 인스턴스 생성
        item = form.save()

        # Content 모델 인스턴스 생성
        content = Content.objects.create(
            content_type=content_type,
            object_id=item.id
        )

        post_content = PostContent.objects.create(
            post_id=request.POST.get('post'),
            content=content
        )

        return HttpResponse({
            "content_id": content.id,
            "content_type": content_type.model,
            "preview": str(item)
        })

    return HttpResponse({"error": form.errors}, status=400)


class DeleteContentView(View):
    def delete(self, request, pk):
        post_content = get_object_or_404(PostContent, pk=pk)
        content = post_content.content
        item = content.item
        post_content.delete()
        item.delete()
        content.delete()
        return HttpResponse(status=200)


## Post Options CRUDViews
class PostOptionListView(ListView):
    model = PostOptions
    template_name = 'basiccontent/postoptions/post_option_list.html'
    context_object_name = 'post_options'

    def get_queryset(self):
        subpost_id = self.kwargs.get('subpost_id')
        post_options = PostOptions.objects.filter(post__in=[subpost_id]).prefetch_related('post').order_by('option_order')
        return post_options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subpost_id'] = self.kwargs.get('subpost_id')
        context['subpost_first'] = SubPost.objects.filter(id=self.kwargs.get('subpost_id')).first()
        return context

class PostOptionCreateView(CreateView):
    model = PostOptions
    form_class = PostOptionsForm
    template_name = 'basiccontent/postoptions/post_option_form.html'
    context_object_name = 'post_options'

    def get_initial(self):
        initial = super().get_initial()
        subpost_id = self.kwargs.get('subpost_id')  # URL 경로 매개변수에서 가져옵니다
        if subpost_id:
            initial['post'] = [subpost_id]  # ManyToManyField에 대한 초기값은 리스트로 제공
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            subpost_id = self.kwargs.get('subpost_id')
            post_options = PostOptions.objects.filter(post__in=[subpost_id]).prefetch_related('post').order_by('option_order')
            return render(self.request, 'basiccontent/postoptions/post_option_list_partials.html', {'post_options': post_options})
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subpost_id'] = self.kwargs.get('subpost_id')
        return context

    def get_success_url(self):
        if self.request.headers.get('HX-Request'):
            return self.request.path
        return super().get_success_url()


class PostOptionUpdateView(UpdateView):
    model = PostOptions
    form_class = PostOptionsForm
    template_name = 'basiccontent/postoptions/post_option_form.html'
    context_object_name = 'post_options'

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            subpost_id = self.kwargs.get('subpost_id')
            post_options = PostOptions.objects.filter(post__in=[subpost_id]).prefetch_related('post').order_by('option_order')
            return render(self.request, 'basiccontent/postoptions/post_option_list_partials.html', {'post_options': post_options})
        return response

    def get_success_url(self):
        if self.request.headers.get('HX-Request'):
            return self.request.path
        return super().get_success_url()


class PostOptionDeleteView(DeleteView):
    model = PostOptions

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        subpost_id = self.object.post.first().id  # 삭제 전에 subpost_id 저장
        self.object.delete()

        if self.request.headers.get('HX-Request'):
            post_options = PostOptions.objects.filter(post__in=[subpost_id]).order_by('option_order')
            return render(self.request, 'basiccontent/postoptions/post_option_list_partials.html', {'post_options': post_options})
        return super().delete(request, *args, **kwargs)



## User Answer CRUD Views
class UserProfileCreateView(CreateView):
    """사용자 정보를 입력받는 뷰"""
    model = User
    form_class = UserProfileForm
    template_name = 'basiccontent/user_answer/user_profile_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_post_id'] = self.kwargs.get('main_post_id')
        return context

    def form_valid(self, form):
        # privacy_agreement 필드는 모델에 없으므로 제거
        privacy_agreement = form.cleaned_data.pop('privacy_agreement', None)

        # 동의하지 않은 경우 폼 제출 거부
        if not privacy_agreement:
            form.add_error('privacy_agreement', '개인정보 수집 및 이용에 동의해야 설문에 참여할 수 있습니다.')
            return self.form_invalid(form)

        # 사용자 정보 저장
        user = form.save()

        # 세션에 사용자 ID 저장
        self.request.session['user_id'] = user.id

        main_post_id = self.kwargs.get('main_post_id')

        # 접근 로그 기록
        AccessLog.objects.create(
            user=user,
            action='로그인',
            ip_address=self.request.META.get('REMOTE_ADDR', '')
        )

        if main_post_id:
            # 전체 페이지 리다이렉트가 필요함을 HTMX에 알려줌
            response = redirect('basiccontent:answer_list', main_post_id=main_post_id)
            response['HX-Redirect'] = response.url
            return response
        return HttpResponse("잘못된 접근입니다.", status=403)


class UserAnswerListView(ListView):
    model = SubPost
    template_name = 'basiccontent/user_answer/user_answer_submit.html'
    context_object_name = 'sub_posts'

    def get_queryset(self):
        main_post_id = self.kwargs.get('main_post_id')
        sub_posts = SubPost.objects.filter(main_post_id=main_post_id).select_related('main_post', 'post_type').prefetch_related(
            Prefetch(
                'postoptions_set',
                queryset=PostOptions.objects.all().order_by('option_order')
            ),
            Prefetch(
                'useranswer_set',
                queryset=UserAnswer.objects.all().select_related('user').prefetch_related('multisubjectiveanswers_set')
            )
        )
        return sub_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 세션에서 사용자 ID 가져오기
        user_id = self.request.session.get('user_id')

        # 사용자가 없으면 사용자 정보 입력 페이지로 리다이렉트
        if not user_id:
            return redirect('basiccontent:user-profile', main_post_id=self.kwargs.get('main_post_id'))

        # 사용자 객체 가져오기
        user = get_object_or_404(User, id=user_id)

        # 접근 로그 기록
        AccessLog.objects.create(
            user=user,
            action='설문 접근',
            ip_address=self.request.META.get('REMOTE_ADDR', '')
        )

        # 현재 사용자의 기존 답변 가져오기
        for sub_post in context['sub_posts']:
            # 사용자 답변 가져오기 (없으면 생성)
            user_answer, created = UserAnswer.objects.get_or_create(
                user=user,
                post=sub_post,
                defaults={'subjective_answer': '', 'answer': None}
            )

            # 주관식(다중서술형)인 경우 다중 답변 생성
            if sub_post.post_type.post_type == '주관식(다중서술형)':
                # 다중 답변이 없으면 3개 생성
                multi_answers = MultiSubjectiveAnswers.objects.filter(user_answer=user_answer)
                if not multi_answers.exists():
                    for i in range(1, 4):
                        MultiSubjectiveAnswers.objects.create(
                            user_answer=user_answer,
                            answer_number=i,
                            answer_description=''
                        )

                # 다중 답변 가져오기
                sub_post.multisubjectiveanswers_set = MultiSubjectiveAnswers.objects.filter(
                    user_answer=user_answer
                ).order_by('answer_number')

            # 현재 사용자의 답변 저장
            sub_post.user_answer = user_answer

            sub_post.selected_answer_id = user_answer.answer.id if user_answer.answer else None
            sub_post.subjective_answer_text = user_answer.subjective_answer

            # 사용자 정보도 컨텍스트에 추가
        context['user'] = user

        return context

    def get_success_url(self):
        return reverse_lazy('basiccontent:post-end')


    @method_decorator(prevent_resubmission)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class UserAnswerUpdateView(UpdateView):
    model = UserAnswer
    fields = ['answer', 'subjective_answer']

    def get_object(self):
        user_id = self.request.session.get('user_id')
        if not user_id:
            return None

        # SubPost ID 가져오기
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(SubPost, id=post_id)

        # 사용자 답변 가져오기 (없으면 생성)
        user_answer, created = UserAnswer.objects.get_or_create(
            user_id=user_id,
            post=post,
            defaults={'subjective_answer': '', 'answer': None}
        )

        return user_answer

    def form_valid(self, form):
        response = super().form_valid(form)

        # 최종 제출인 경우 User.is_completed를 True로 설정
        if self.request.POST.get('final_submit') == 'true':
            user_id = self.request.session.get('user_id')
            if user_id:
                User.objects.filter(id=user_id).update(is_completed=True)

                # 접근 로그 기록
                AccessLog.objects.create(
                    user_id=user_id,
                    action='설문 제출 완료',
                    ip_address=self.request.META.get('REMOTE_ADDR', '')
                )

        # HTMX 요청인 경우
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=200, content='저장 완료')

        return response

    def get_success_url(self):
        # post = self.object.post
        # main_post_id = post.main_post_id
        # return reverse_lazy('basiccontent:answer_list', kwargs={'main_post_id': main_post_id})
        if self.request.POST.get('final_submit') == 'true':
            return reverse_lazy('basiccontent:post-end')

        post = self.object.post
        main_post_id = post.main_post_id
        return reverse_lazy('basiccontent:answer_list', kwargs={'main_post_id': main_post_id})


class MultiSubjectiveUpdateView(UpdateView):
    """다중 주관식 답변을 저장하는 뷰 (HTMX 호출용)"""
    model = MultiSubjectiveAnswers
    fields = ['answer_number', 'answer_description']
    template_name = 'basiccontent/user_answer/multi_subjective_answers_form.html'

    def form_valid(self, form):
        # 폼 저장
        self.object = form.save()

        # HTMX 요청인 경우
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=200, content='저장 완료')

        return super().form_valid(form)

    def get_success_url(self):
        post = self.object.post
        main_post_id = post.main_post_id
        return reverse_lazy('basiccontent:answer_list', kwargs={'main_post_id': main_post_id})



# class EndTemplateView(TemplateView):
#     template_name = 'basiccontent/end_template.html'


class EndTemplateView(View):
    """설문 완료 페이지를 보여주는 뷰"""

    def get(self, request, *args, **kwargs):
        # 세션 초기화
        if 'user_id' in request.session:
            del request.session['user_id']

        return render(request, 'basiccontent/end_template.html')


# 유저에게 설문 배포하기
def generate_survey_link(request, post_id):
    """암호화된 설문 링크 생성"""
    # 기존 링크가 있으면 가져오고, 없으면 새로 생성
    survey_link, created = SurveyLink.objects.get_or_create(
        main_post_id=post_id,
        is_used=False,
        expires_at__gt=timezone.now(),
        defaults={'main_post_id': post_id}
    )

    # 암호화된 URL 생성
    survey_url = request.build_absolute_uri(
        reverse('basiccontent:survey-redirect', kwargs={'uuid': survey_link.uuid})
    )

    # return HttpResponse(f"<div>{survey_url}</div>")
    return render(request, "basiccontent/generate_survey_link.html", {
        'survey_url': survey_url,
    })

    # return JsonResponse({'url': survey_url})


def survey_redirect(request, uuid):
    """암호화된 UUID로 접근 시 적절한 설문으로 리다이렉트"""
    try:
        survey_link = SurveyLink.objects.get(uuid=uuid)

        # 링크 유효성 확인
        if not survey_link.is_valid():
            messages.error(request, "설문 링크가 만료되었거나 이미 사용되었습니다.")
            return redirect('basiccontent:post-list')

        # 링크를 사용됨으로 표시 (일회용으로 사용하려면 주석 해제)
        # survey_link.mark_as_used()

        # 적절한 프로필 페이지로 리다이렉트
        return redirect('basiccontent:user-profile', main_post_id=survey_link.main_post_id)

    except SurveyLink.DoesNotExist:
        messages.error(request, "유효하지 않은 설문 링크입니다.")
        return redirect('basiccontent:post-list')
