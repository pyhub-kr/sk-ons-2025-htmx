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
    path('subposts/<int:post_id>/list/', views.SubPostListView.as_view(), name='subpost-list'),
    path('subposts/<int:post_id>/create/', views.SubPostCreateView.as_view(), name='subpost-create'),
    path('subposts/<int:pk>/update/', views.SubPostUpdateView.as_view(), name='subpost-update'),
    path('subposts/<int:pk>/delete/', views.SubPostDeleteView.as_view(), name='subpost-delete'),

    # contents
    path('posts/<int:pk>/contents/', views.PostContentUpdateView.as_view(), name='post-content-update'),
    path('contents/get-form/', views.get_content_form, name='get-content-form'),
    path('contents/create/', views.create_content, name='create-content'),
    path('contents/<int:pk>/delete/', views.DeleteContentView.as_view(), name='delete-content'),

    # post options
    path('posts/option/<int:subpost_id>/list/', views.PostOptionListView.as_view(), name='option-list'),
    path('posts/option/<int:subpost_id>/create/', views.PostOptionCreateView.as_view(), name='option-create'),
    path('posts/option/<int:pk>/update/', views.PostOptionUpdateView.as_view(), name='option-update'),
    path('posts/option/<int:pk>/delete/', views.PostOptionDeleteView.as_view(), name='option-delete'),

    ## User Answer CRUD
    # 유저 정보 입력
    path('user/profile/<int:main_post_id>/', views.UserProfileCreateView.as_view(), name='user-profile'),
    # 메인 포스트별 서브포스트 목록 및 설문지 표시
    path('user/answer/<int:main_post_id>/', views.UserAnswerListView.as_view(), name='answer_list'),

    # 사용자 답변 제출 처리
    path('user/answer/submit/', views.UserAnswerUpdateView.as_view(), name='submit-user-answer'),
    path('user/answer/submit/<int:pk>/', views.UserAnswerUpdateView.as_view(), name='submit-user-answer'),
    path('user/multisubj/submit/<int:pk>/', views.MultiSubjectiveUpdateView.as_view(), name='multi-subjective-answers'),

    path('post/end/', views.EndTemplateView.as_view(), name='post-end'),

    # 유저에게 설문 배포하기
    # 암호화된 링크 생성 및 리다이렉트 URL
    path('surveys/generate-link/<int:post_id>/', views.generate_survey_link, name='generate-survey-link'),
    path('surveys/s/<uuid:uuid>/', views.survey_redirect, name='survey-redirect'),

]


