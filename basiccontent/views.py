from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

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
class UserAnswerListView(ListView):
    model = SubPost
    template_name = 'basiccontent/user_answer/user_answer_submit.html'
    context_object_name = 'sub_posts'

    def get_queryset(self):
        # 메인 포스트 ID를 URL로부터 가져옴
        main_post_id = self.kwargs.get('main_post_id')
        # 만약 main_post_id가 없다면 모든 SubPost를 반환
        if main_post_id:
            return SubPost.objects.filter(main_post_id=main_post_id).order_by('id')
        return SubPost.objects.all().order_by('main_post', 'id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_post_id = self.kwargs.get('main_post_id')

        if main_post_id:
            context['main_post'] = get_object_or_404(MainPost, id=main_post_id)

        # 사용자 정보 폼 추가
        context['user_form'] = UserProfileForm(self.request.POST or None)

        # 각 SubPost에 대한 UserAnswerForm 생성
        context['answer_forms'] = {}
        for sub_post in context['sub_posts']:
            context['answer_forms'][sub_post.id] = UserAnswerForm(post=sub_post)

            # PostOptions 정보 추가
            post_options = PostOptions.objects.filter(post=sub_post).order_by('option_order')
            context['answer_forms'][sub_post.id].options = post_options

        return context


class SubmitUserAnswerView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        sub_post_id = request.POST.get('sub_post_id')
        sub_post = get_object_or_404(SubPost, id=sub_post_id)

        # 사용자 정보 확인 또는 생성
        user_id = request.session.get('user_id')
        if not user_id:
            # 사용자 정보 폼 검증
            user_form = UserProfileForm(request.POST)
            if user_form.is_valid():
                # 사용자 생성 또는 검색
                username = user_form.cleaned_data['username']
                phone_number = user_form.cleaned_data['phone_number']

                try:
                    user, created = User.objects.get_or_create(
                        phone_number=phone_number,
                        defaults={
                            'username': username,
                            'birthday': user_form.cleaned_data['birthday'],
                            'gender': user_form.cleaned_data['gender']
                        }
                    )
                    request.session['user_id'] = user.id
                except Exception as e:
                    return JsonResponse({'success': False, 'message': str(e)})
            else:
                return JsonResponse({'success': False, 'errors': user_form.errors})
        else:
            user = get_object_or_404(User, id=user_id)

        # 답변 폼 검증
        form = UserAnswerForm(request.POST, post=sub_post)
        if form.is_valid():
            # 기존 답변이 있는지 확인
            user_answer, created = UserAnswer.objects.get_or_create(
                user=user,
                post=sub_post,
                defaults={
                    'answer': form.cleaned_data.get('answer'),
                    'subjective_answer': form.cleaned_data.get('subjective_answer')
                }
            )

            # 기존 답변이 있었다면 업데이트
            if not created:
                user_answer.answer = form.cleaned_data.get('answer')
                user_answer.subjective_answer = form.cleaned_data.get('subjective_answer')
                user_answer.save()

            # 다중 주관식 답변 처리
            if sub_post.post_type.post_type == '다중주관식':
                formset = MultiSubjectiveAnswerFormSet(request.POST, instance=user_answer)
                if formset.is_valid():
                    formset.save()
                else:
                    return JsonResponse({'success': False, 'errors': formset.errors})

            # 다음 문항이 있는지 확인
            next_sub_post = SubPost.objects.filter(
                main_post=sub_post.main_post,
                id__gt=sub_post.id
            ).order_by('id').first()

            if next_sub_post:
                # 다음 문항으로 이동
                return JsonResponse({
                    'success': True,
                    'redirect': f'#question-{next_sub_post.id}'
                })
            else:
                # 설문 완료
                messages.success(request, '설문에 응답해주셔서 감사합니다.')
                return JsonResponse({
                    'success': True,
                    'complete': True,
                    'message': '설문이 완료되었습니다. 감사합니다.'
                })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})