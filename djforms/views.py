from typing import Generator

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .form_template_fields import get_field_type_choices
from .models import FormTemplate, FormTemplateField, FormResponse, FormResponseField
from .forms import (
    FormTemplateForm,
    FormTemplateFieldForm,
)


@staff_member_required
def form_template_list(request):
    formtemplate_list = FormTemplate.objects.all()
    return render(
        request,
        "djforms/formtemplate_list.html",
        {"formtemplate_list": formtemplate_list},
    )


@staff_member_required
def form_template_new(request):
    data = {"title": "제목 없는 설문지"}
    form = FormTemplateForm(data=data)
    assert form.is_valid()
    form_template = form.save()
    return redirect("djforms:form_template_edit", pk=form_template.pk)


@staff_member_required
def form_template_edit(request, pk):
    form_template = get_object_or_404(FormTemplate, pk=pk)

    form_template_field_form_list = []
    form_template_field_qs = form_template.field_set.all().order_by("order")

    if request.method == "POST":
        form_template_form = FormTemplateForm(
            data=request.POST, files=request.FILES, instance=form_template
        )
        if form_template_form.is_valid():
            form_template_form.save()

        for form_template_field in form_template_field_qs:
            form = FormTemplateFieldForm(
                data=request.POST, files=request.FILES, instance=form_template_field
            )
            if form.is_valid():
                form.save()

            form_template_field_form_list.append(form)

        is_all_valid = form_template_form.is_valid() and all(
            form.is_valid() for form in form_template_field_form_list
        )
        if is_all_valid:
            messages.success(request, "모든 필드의 유효성 검사를 통과했습니다.")

    else:
        form_template_form = FormTemplateForm(instance=form_template)
        for form_template_field in form_template_field_qs:
            form = FormTemplateFieldForm(instance=form_template_field)
            form_template_field_form_list.append(form)

    rendered_form_template_field_form_list: Generator[str] = (
        form.render_template(request) for form in form_template_field_form_list
    )

    return render(
        request,
        "djforms/formtemplate_form.html",
        {
            "form_template": form_template,
            "form_template_form": form_template_form,
            "rendered_form_template_field_form_list": rendered_form_template_field_form_list,
            "field_type_choices": get_field_type_choices(),
        },
    )


@staff_member_required
def form_template_delete(request, pk):
    raise NotImplementedError


@require_GET
@login_required
def form_template_field_new(request, form_template_pk: int) -> HttpResponse:
    field_type_name = request.GET.get("field_type_name", "text")
    form_template = get_object_or_404(FormTemplate, pk=form_template_pk)

    form = FormTemplateFieldForm(data={})
    assert form.is_valid(), f"Form validation failed: {form.errors}"
    form_template_field = form.save(commit=False)
    form_template_field.form_template = form_template
    form_template_field.field_type = field_type_name
    form_template_field.save()

    form = FormTemplateFieldForm(instance=form_template_field)
    return HttpResponse(form.render_template(request=request))


@require_http_methods(["DELETE"])
@login_required
def form_template_field_delete(request, form_template_pk: int, pk: int):
    qs = FormTemplateField.objects.filter(pk=pk, form_template__pk=form_template_pk)
    form_template_field = qs.first()
    if form_template_field is not None:
        form_template_field.delete()
    # 204 응답을 하면, htmx는 swap 동작을 하지 않습니다. 200 응답만 OK.
    return HttpResponse()


@require_POST
@login_required
def form_template_field_reorder(request, form_template_pk):
    form_template = get_object_or_404(FormTemplate, pk=form_template_pk)

    field_ids = request.POST.getlist("field_ids")
    for order, field_id in enumerate(field_ids):
        qs = FormTemplateField.objects.filter(id=field_id, form_template=form_template)
        qs.update(order=order)
    return HttpResponse()


def form_response_new(request, form_pk):
    """폼 제출"""
    form = get_object_or_404(FormTemplate, id=form_pk, is_published=True)

    if not form.allow_anonymous and not request.user.is_authenticated:
        raise PermissionDenied

    if form.expires_at and form.expires_at < timezone.now():
        messages.error(request, "이 폼은 만료되었습니다.")
        return redirect("djforms:form_template_list")

    if request.method == "POST":
        submission = FormResponse.objects.create(
            form=form,
            # user=request.user if request.user.is_authenticated else None,
            # is_anonymous=not request.user.is_authenticated,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        for field in form.field_set.all():
            value = request.POST.get(f"field_{field.id}")
            file = request.FILES.get(f"field_{field.id}")

            if value or file:
                FormResponseField.objects.create(
                    submission=submission, field=field, value=value, file=file
                )

        messages.success(request, "폼이 성공적으로 제출되었습니다.")
        return redirect("djforms:form_submit_success", submission_id=submission.id)

    return render(request, "djforms/form_submit.html", {"form": form})


def form_response_created(request, submission_id):
    """폼 제출 완료"""
    submission = get_object_or_404(FormSubmission, id=submission_id)
    return render(
        request, "djforms/form_submit_success.html", {"submission": submission}
    )
