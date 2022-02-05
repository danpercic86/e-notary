import datetime
from typing import Tuple, Dict

from django.contrib.admin import ModelAdmin, register
from django.forms import ModelForm, FileField, FileInput
from django.shortcuts import redirect
from faker import Faker

from common.models import Example, Client, IdUpload, Template


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
    readonly_fields = ("generated_doc",) + BaseModelAdmin.readonly_fields
    list_display = ("__str__", "template", "generated_doc")


@register(IdUpload)
class IdUploadAdmin(ModelAdmin):
    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        return False

    def save_model(self, request, obj: IdUpload, form, change: bool) -> None:
        client = Client()
        fake = Faker()
        client.first_name = fake.first_name()
        client.last_name = fake.last_name()
        client.birthday = datetime.datetime.now()
        client.id_emitted_at = datetime.datetime.now()
        client.id_emitted_by = fake.name()
        client.id_number = fake.random.randint(100000, 99999999)
        client.id_series = client.first_name[0] + client.last_name[0]
        client.cnp = fake.unique.random_int(min=1000000000000, max=6999999999999)
        client.residence = fake.address()
        client.created = datetime.datetime.now()
        client.modified = datetime.datetime.now()
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
    readonly_fields = ("file",) + BaseModelAdmin.readonly_fields
    form = TemplatesForm
