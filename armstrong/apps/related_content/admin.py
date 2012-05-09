from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.forms import widgets as django_widgets

from armstrong.hatband import widgets

from .models import RelatedContent
from .models import RelatedType

from armstrong.hatband.utils import static_url


"""
Setting ARMSTRONG_RELATED_TYPE_DEFAULT_FILTER allows you to specify
values to provide to ``get`` that looks up the initial value for
"""
RELATED_TYPE_INITIAL_FILTER = "ARMSTRONG_RELATED_TYPE_INITIAL_FILTER"


class RelatedContentInlineForm(forms.ModelForm):

    class Media:
        js = (
            'hatband/js/jquery-ui-1.8.16.min.js',
          )

    class Meta:
        widgets = {
            "destination_id": widgets.RawGenericKeyWidget(
                object_id_name="destination_id",
                content_type_name="destination_type",
            ),
            "order": django_widgets.HiddenInput(),
        }


class RelatedContentInline(GenericTabularInline):
    ct_field = "source_type"
    ct_fk_field = "source_id"

    model = RelatedContent
    template = 'admin/edit_inline/related_content.html'
    form = RelatedContentInlineForm

    extra = 0

    def formfield_for_foreignkey(self, *args, **kwargs):
        args, kwargs = formfield_for_foreignkey_helper(self, *args, **kwargs)
        return super(RelatedContentInline, self).formfield_for_foreignkey(
                *args, **kwargs)


def formfield_for_foreignkey_helper(inline, *args, **kwargs):
    """
    The implementation for ``RelatedContentInline.formfield_for_foreignkey``

    This takes the takes all of the ``args`` and ``kwargs`` from the call to
    ``formfield_for_foreignkey`` and operates on this.  It returns the updated
    ``args`` and ``kwargs`` to be passed on to ``super``.

    This is solely an implementation detail as it's easier to test a function
    than to provide all of the expectations that the ``GenericTabularInline``
    has.
    """
    db_field = args[0]
    if db_field.name != "related_type":
        return args, kwargs

    initial_filter = getattr(settings, RELATED_TYPE_INITIAL_FILTER,
            False)
    if "initial" not in kwargs and initial_filter:
        # TODO: handle gracefully if unable to load and in non-debug
        initial = RelatedType.objects.get(**initial_filter).pk
        kwargs["initial"] = initial
    return args, kwargs


admin.site.register(RelatedType)
