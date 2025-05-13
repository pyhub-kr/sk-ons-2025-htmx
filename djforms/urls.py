from django.urls import path
from . import views

app_name = "djforms"

urlpatterns = (
    [
        # 폼 관리
        path("", views.form_template_list, name="form_template_list"),
        path("new/", views.form_template_new, name="form_template_new"),
        path("<int:pk>/", views.form_template_edit, name="form_template_detail"),
        path("<int:pk>/edit/", views.form_template_edit, name="form_template_edit"),
        path(
            "<int:pk>/delete/", views.form_template_delete, name="form_template_delete"
        ),
    ]
    + [
        # 필드 관리
        path(
            "<int:form_template_pk>/fields/new/",
            views.form_template_field_new,
            name="form_template_field_new",
        ),
        path(
            "<int:form_template_pk>/fields/<int:pk>/delete/",
            views.form_template_field_delete,
            name="form_template_field_delete",
        ),
        path(
            "<int:form_template_pk>/fields/reorder/",
            views.form_template_field_reorder,
            name="form_template_field_reorder",
        ),
    ]
    + [
        # 폼 제출
        path(
            "<int:form_template_pk>/responses/new/",
            views.form_response_new,
            name="form_response_new",
        ),
        path(
            "response/<int:form_response_pk>/success/",
            views.form_response_created,
            name="form_response_created",
        ),
    ]
)
