import datetime
from typing import Tuple, Dict

import faker as faker
from django.contrib.admin import ModelAdmin, register
from faker import Faker

from common.models import Example, Client, IdUpload


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
    pass


@register(IdUpload)
class IdUploadAdmin(ModelAdmin):
    def save_model(self, request, obj:IdUpload, form, change:bool)->None:
        client= Client()
        fake = Faker()
        client.first_name = fake.first_name()
        client.last_name = fake.last_name()
        client.birthday = datetime.datetime.now()
        client.id_emitted_at = fake.id_emitted_at()
        client.id_emitted_by = fake.id_emitted_by()
        client.id_number = fake.random.randint(10000,999999)
        client.id_emitted_at = fake.id_emitted_at()
        client.cnp = fake.unique.random_int(min=1000000000000,max=6999999999999)
        client.residence = fake.address()
        client.id_series = client.first_name[0] + client.last_name[0]
        client.created = datetime.datetime.now()
        client.modified = datetime.datetime.now()
        client.face=obj.face
        client.back=obj.back
        client.save()
        print(obj.back)
