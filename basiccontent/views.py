from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

from basiccontent.models import *
from basiccontent.forms import *
from django.contrib.contenttypes.models import ContentType
from django.views.generic import *

## BasicPost CRUD Views
class BasicPostListView(ListView):
    model = BasicPost
    template_name = 'basiccontent/post_list.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_type'] = ContentType.objects.all()
        return context


class BasicPostCreateView(CreateView):
    model = BasicPost
    form_class = BasicPostForm
    template_name = 'basiccontent/post_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            posts = BasicPost.objects.all()
            return render(self.request, 'basiccontent/partials/post_list_partials.html', {'posts': posts})
        return response

    def get_success_url(self):
        if self.request.headers.get('HX-Request'):
            return self.request.path
        return super().get_success_url()


class BasicPostUpdateView(UpdateView):
    model = BasicPost
    form_class = BasicPostForm
    template_name = 'basiccontent/post_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            posts = BasicPost.objects.all()
            return render(self.request, 'basiccontent/partials/post_list_partials.html', {'posts': posts})
        return response

    def get_success_url(self):
        if self.request.headers.get('HX-Request'):
            return self.request.path
        return super().get_success_url()


class BasicPostDeleteView(DeleteView):
    model = BasicPost

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if self.request.headers.get('HX-Request'):
            posts = BasicPost.objects.all()
            return render(self.request, 'basiccontent/partials/post_list_partials.html', {'posts': posts})
        return super().delete(request, *args, **kwargs)


## Content CRUD Views
class PostContentUpdateView(UpdateView):
    model = BasicPost
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