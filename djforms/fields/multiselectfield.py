from collections import UserList
from typing import Optional, Union

from django import forms
from django.db import models
from django.core import exceptions, validators
from django.db.models.sql.query import Query
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


class MaxValueMultiFieldValidator(validators.MaxLengthValidator):
    code = "max_multifield_value"

    def clean(self, x):
        return len(",".join(x))


class MinChoicesValidator(validators.MinLengthValidator):
    message = _("You must select a minimum of  %(limit_value)d choices.")
    code = "min_choices"


class MaxChoicesValidator(validators.MaxLengthValidator):
    message = _("You must select a maximum of  %(limit_value)d choices.")
    code = "max_choices"


class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.min_choices = kwargs.pop("min_choices", None)
        self.max_choices = kwargs.pop("max_choices", None)
        self.max_length = kwargs.pop("max_length", None)
        self.flat_choices = kwargs.pop("flat_choices")
        super(MultiSelectFormField, self).__init__(*args, **kwargs)
        self.max_length = get_max_length(self.choices, self.max_length)
        self.validators.append(MaxValueMultiFieldValidator(self.max_length))
        if self.max_choices is not None:
            self.validators.append(MaxChoicesValidator(self.max_choices))
        if self.min_choices is not None:
            self.validators.append(MinChoicesValidator(self.min_choices))

    def to_python(self, value):
        return MSFList(
            dict(self.flat_choices), super(MultiSelectFormField, self).to_python(value)
        )


def get_max_length(choices, max_length, default=200):
    if max_length is None:
        if choices:
            return len(",".join([str(key) for key, label in choices]))
        else:
            return default
    return max_length


class _FakeSqlVal(UserList):

    contains_aggregate = False
    contains_column_references = False
    contains_over_clause = False

    def __str__(self):
        return ",".join(map(str, self))


class MSFList(list):

    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super(MSFList, self).__init__(*args, **kwargs)

    def __str__(msgl):
        msg_list = [
            msgl.choices.get(int(i)) if i.isdigit() else msgl.choices.get(i)
            for i in msgl
        ]
        return ", ".join(str(s) for s in msg_list)

    def resolve_expression(
        self,
        query: Query = None,
        allow_joins: bool = True,
        reuse: Optional[bool] = None,
        summarize: bool = False,
        for_save: bool = False,
    ) -> Union[list, _FakeSqlVal]:
        if for_save:
            result = _FakeSqlVal(self)
        else:
            result = list(self)
        return result


class MultiSelectField(models.CharField):
    """Choice values can not contain commas."""

    def __init__(self, *args, **kwargs):
        self.min_choices = kwargs.pop("min_choices", None)
        self.max_choices = kwargs.pop("max_choices", None)
        super(MultiSelectField, self).__init__(*args, **kwargs)
        self.max_length = get_max_length(self.choices, self.max_length)
        self.validators[0] = MaxValueMultiFieldValidator(self.max_length)
        if self.min_choices is not None:
            self.validators.append(MinChoicesValidator(self.min_choices))
        if self.max_choices is not None:
            self.validators.append(MaxChoicesValidator(self.max_choices))

    def _get_flatchoices(self):
        l = super(MultiSelectField, self)._get_flatchoices()

        class MSFFlatchoices(list):
            # Used to trick django.contrib.admin.utils.display_for_field into
            # not treating the list of values as a dictionary key (which errors
            # out)
            def __bool__(self):
                return False

            __nonzero__ = __bool__

        return MSFFlatchoices(l)

    flatchoices = property(_get_flatchoices)

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def get_choices_selected(self, arr_choices):
        named_groups = arr_choices and isinstance(arr_choices[0][1], (list, tuple))
        choices_selected = []
        if named_groups:
            for choice_group_selected in arr_choices:
                for choice_selected in choice_group_selected[1]:
                    choices_selected.append(str(choice_selected[0]))
        else:
            for choice_selected in arr_choices:
                choices_selected.append(str(choice_selected[0]))
        return choices_selected

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if opt_select not in arr_choices:
                raise exceptions.ValidationError(
                    self.error_messages["invalid_choice"] % {"value": value}
                )

    def get_default(self):
        default = super(MultiSelectField, self).get_default()
        if isinstance(default, int):
            default = str(default)
        return default

    def formfield(self, **kwargs):
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "choices": self.choices,
            "max_length": self.max_length,
            "max_choices": self.max_choices,
            "flat_choices": self.choices,
        }
        if self.has_default():
            defaults["initial"] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_prep_value(self, value):
        return "" if value is None else ",".join(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared and not isinstance(value, str):
            value = self.get_prep_value(value)
        return value

    def to_python(self, value):
        choices = dict(self.flatchoices)

        if value:
            return (
                value if isinstance(value, list) else MSFList(choices, value.split(","))
            )
        return MSFList(choices, [])

    def from_db_value(self, value, expression, connection, *args):
        if value is None:
            return value
        return self.to_python(value)

    def contribute_to_class(self, cls, name, private_only=False):
        super(MultiSelectField, self).contribute_to_class(cls, name, private_only)
        if self.choices:

            def get_list(obj):
                fieldname = name
                choicedict = dict(self.choices)
                display = []
                if getattr(obj, fieldname):
                    for value in getattr(obj, fieldname):
                        item_display = choicedict.get(value, None)
                        if item_display is None:
                            try:
                                item_display = choicedict.get(int(value), value)
                            except (ValueError, TypeError):
                                item_display = value
                        display.append(str(item_display))
                return display

            def get_display(obj):
                return ", ".join(get_list(obj))

            get_display.short_description = self.verbose_name

            setattr(cls, "get_%s_list" % self.name, get_list)
            setattr(cls, "get_%s_display" % self.name, get_display)
