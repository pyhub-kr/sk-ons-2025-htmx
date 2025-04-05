from django.urls import path
from . import views

urlpatterns = [
    path('content/create/', views.ContentCreateView.as_view(), name='content_create'),
    path('htmx/add-media-form/', views.add_media_form, name='add_media_form'),
    path('htmx/add-question-form/', views.add_question_form, name='add_question_form'),
    path('htmx/add-choice-form/<int:question_id>/', views.add_choice_form, name='add_choice_form'),
    path('htmx/toggle-media-fields/', views.toggle_media_fields, name='toggle_media_fields'),
    path('htmx/toggle-question-fields/', views.toggle_question_fields, name='toggle_question_fields'),
]