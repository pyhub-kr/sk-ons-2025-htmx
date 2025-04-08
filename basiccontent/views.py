from django.db.models import Prefetch
from django.http import HttpResponse
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
        posts = MainPost.objects.filter(id=post_id)
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
            post_options = PostOptions.objects.all()
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
            post_options = PostOptions.objects.all()
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

