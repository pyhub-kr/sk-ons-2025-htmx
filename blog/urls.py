from django.urls import path
from . import views

# URL Reverse 시에 사용되는 namespace : "blog:index"
app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.post_new, name="post_new"),
]
