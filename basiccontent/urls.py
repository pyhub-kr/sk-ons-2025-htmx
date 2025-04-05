from django.urls import path
from basiccontent import views


app_name = "basiccontent"

urlpatterns = [

    # BasicPost CRUD
    path('posts/list/', views.BasicPostListView.as_view(), name='post-list'),
    path('posts/create/', views.BasicPostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/update/', views.BasicPostUpdateView.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', views.BasicPostDeleteView.as_view(), name='post-delete'),


    # contents
    path('posts/<int:pk>/contents/', views.PostContentUpdateView.as_view(), name='post-content-update'),
    path('contents/get-form/', views.get_content_form, name='get-content-form'),
    path('contents/create/', views.create_content, name='create-content'),
    path('contents/<int:pk>/delete/', views.DeleteContentView.as_view(), name='delete-content'),

    # post options
    path('posts/option/<int:pk>/list/', views.BasicPostListView.as_view(), name='option-list'),

]


