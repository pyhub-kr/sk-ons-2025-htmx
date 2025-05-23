from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic.list import ListView

from blog.forms import PostForm
from blog.models import Post


# def index(request):
#     pass

class PostListView(ListView):
    model = Post
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            return "blog/post_list.html#post-list"
        return super().get_template_names()


index = PostListView.as_view(
    # model=Post,
    # paginate_by=10,  # ?page=1
)

# def post_new(request):
#     pass

# 함수를 생성해주는 클래스


class ModalCreateView(CreateView):
    template_name = "modal-form.html"
    partial_template_name = "modal-form.html#form"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["form_url"] = self.request.path
        return context_data

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save()
        messages.success(self.request, "생성되었습니다.")
        response = render(self.request, self.partial_template_name, {
            "object": self.object,
            "form": form,
        })
        # TODO: htmx 이벤트
        return response

    def form_invalid(self, form):
        return render(self.request, self.partial_template_name, {
            "object": self.object,
            "form_url": self.request.path,
            "form": form,
        })

    # def get_template_names(self):
    #     if self.request.htmx:
    #         # return "blog/post_form.html#post-form"
    #         return "modal-form.html"
    #     return super().get_template_names()


class PostCreateView(ModalCreateView):
    model = Post
    form_class = PostForm


post_new = PostCreateView.as_view(
    # model=Post,
    # form_class=PostForm,
    # success_url=reverse_lazy("blog:index"),
)
