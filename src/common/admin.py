import os.path
from typing import Tuple, Dict

import pandas
from django.conf import settings
from django.contrib.admin import ModelAdmin, register
from django.forms import ModelForm, FileField, FileInput
from django.shortcuts import redirect
from faker import Faker

from common.models import Example, Client, IdUpload, Template
from common.ocr import ocr


class BaseModelAdmin(ModelAdmin):
    list_filter: Tuple = ("created", "modified")
    readonly_fields: Tuple = ("created", "modified")


class SlugableModelAdmin(ModelAdmin):
    prepopulated_fields: Dict[str, Tuple] = {"slug": ("name",)}


CREATED_MODIFIED = (
    "Created / Modified",
    {
        "fields": ("created", "modified"),
        "description": "Info about the time this entry was added here or updated",
    },
)


@register(Example)
class ExampleAdmin(BaseModelAdmin):
    fieldsets = (
        (None, {"fields": ("name", "status", "status_changed", "published_at")}),
        CREATED_MODIFIED,
    )
    list_display = ("name", "status", "status_changed", "published_at")
    list_editable = ("status",)
    readonly_fields = BaseModelAdmin.readonly_fields + (
        "status_changed",
        "published_at",
    )


@register(Client)
class ClientsAdmin(BaseModelAdmin):
    fieldsets = (
        (
            "Date client",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "cnp",
                    "residence",
                    "birthday",
                    "id_series",
                    "id_number",
                    "id_emitted_by",
                    "id_emitted_at",
                    "registration_number",
                    "face",
                    "back",
                    "template",
                    "generated_doc",
                )
            },
        ),
        (
            "Chitanță",
            {
                "fields": (
                    "cost",
                    "tax",
                    "receipt_series",
                    "receipt_number",
                    "receipt",
                )
            },
        ),
        CREATED_MODIFIED,
    )
    readonly_fields = ("generated_doc", "receipt") + BaseModelAdmin.readonly_fields
    list_display = ("__str__", "template", "generated_doc", "receipt")


@register(IdUpload)
class IdUploadAdmin(ModelAdmin):
    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        return False

    def save_model(self, request, obj: IdUpload, form, change: bool) -> None:
        client = Client()
        fake = Faker()
        result = ocr(
            os.path.join(settings.MEDIA_ROOT, obj.face.name),
            os.path.join(settings.BASE_DIR, "templates", "template.jpeg"),
        )
        client.first_name = result["first_name"]
        client.last_name = result["last_name"]
        client.birthday = pandas.to_datetime(result["birthday"]).date()
        client.id_emitted_at = pandas.to_datetime(result["id_emitted_at"]).date()
        client.id_emitted_by = result["id_emitted_by"]
        client.id_series = result["id_series"][:1]
        client.id_number = result["id_series"][1:]
        client.cnp = fake.unique.random_int(min=1000000000000, max=6999999999999)
        client.residence = fake.address()
        client.cost = obj.cost
        client.tax = obj.tax
        client.registration_number = obj.registration_number
        client.face = obj.face
        client.back = obj.back
        client.template = obj.template
        client.save()
        obj.client = client

    def response_add(self, request, obj, post_url_continue=None):
        return redirect(to=obj.client)


class TemplatesForm(ModelForm):
    file = FileField(
        widget=FileInput(attrs={"accept": "application/docx"}),
        error_messages={"invalid": "Incarcă numai fișiere Microsoft Word (.docx)"},
    )

    class Meta:
        model = Template
        fields = "__all__"


@register(Template)
class TemplatesAdmin(BaseModelAdmin):
    pass
    # form = TemplatesForm
