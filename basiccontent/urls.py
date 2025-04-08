from django.urls import path
from basiccontent import views


app_name = "basiccontent"

urlpatterns = [

    # MainPost CRUD
    path('posts/list/', views.MainPostListView.as_view(), name='post-list'),
    path('posts/create/', views.MainPostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/update/', views.MainPostUpdateView.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', views.MainPostDeleteView.as_view(), name='post-delete'),

    # post + content 확인하기
    path('posts/<int:pk>/detail/', views.MainPostDetailView.as_view(), name='post-detail'),

    # SubPost CRUD
    path('subposts/list/', views.MainPostListView.as_view(), name='subpost-list'),
    path('subposts/create/', views.MainPostCreateView.as_view(), name='subpost-create'),
    path('subposts/<int:pk>/update/', views.MainPostUpdateView.as_view(), name='subpost-update'),
    path('subposts/<int:pk>/delete/', views.MainPostDeleteView.as_view(), name='subpost-delete'),

    # contents
    path('posts/<int:pk>/contents/', views.PostContentUpdateView.as_view(), name='post-content-update'),
    path('contents/get-form/', views.get_content_form, name='get-content-form'),
    path('contents/create/', views.create_content, name='create-content'),
    path('contents/<int:pk>/delete/', views.DeleteContentView.as_view(), name='delete-content'),

    # post options
    path('posts/option/<int:post_id>/list/', views.PostOptionListView.as_view(), name='option-list'),
    path('posts/option/<int:post_id>/create/', views.PostOptionCreateView.as_view(), name='option-create'),
    path('posts/option/<int:pk>/update/', views.PostOptionUpdateView.as_view(), name='option-update'),
    path('posts/option/<int:pk>/delete/', views.PostOptionDeleteView.as_view(), name='option-delete'),

]


