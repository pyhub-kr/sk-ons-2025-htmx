from django.shortcuts import render
from django.urls.base import reverse_lazy
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
post_new = CreateView.as_view(
    model=Post,
    form_class=PostForm,
    success_url=reverse_lazy("blog:index"),
)
