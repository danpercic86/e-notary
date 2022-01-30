import os.path
import re
from typing import final, AnyStr, Final

from django.conf import settings
from django.db.models import (
    Model,
    SlugField,
    CharField,
    PositiveIntegerField,
    DateField,
    ImageField,
    FileField,
)
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from docx import Document as Open
from docx.document import Document
from model_utils import Choices
from model_utils.fields import MonitorField
from model_utils.models import TimeStampedModel, StatusModel

from common.fileds import BigIntegerRangeField


class SlugableModel(Model):
    slug = SlugField(unique=True, db_index=True)

    class Meta:
        abstract = True


class BaseModel(Model):
    class Meta:
        abstract = True

    def get_absolute_url(self) -> AnyStr:
        from django.urls import reverse_lazy

        return reverse_lazy(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=[str(self.id)],
        )

    @property
    def href(self):
        """
        Use this property in admin dashboard to show this object's name as html anchor
        that redirects to object's edit page
        @return:
        """
        from django.utils.html import format_html

        return format_html(f"<a href='{self.get_absolute_url()}'>{self}</a>")


@final
class Example(TimeStampedModel, StatusModel, BaseModel):
    """
    Example model docstring that should be visible in Django documentation
    """

    STATUS: Final[Choices] = Choices("published", "reviewed")

    name = CharField(
        _("example name"),
        max_length=300,
        help_text=_("Some help text that is shown in documentation"),
    )
    published_at = MonitorField(
        _("publishing datetime"), monitor="status", when=["published"], editable=False
    )

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        db_table = "examples"


variables_pattern = re.compile("{{(.*?)}}")


class Client(TimeStampedModel, BaseModel):
    first_name = CharField(max_length=300)
    last_name = CharField(max_length=300)
    cnp = BigIntegerRangeField(min_value=1000000000000, max_value=6999999999999)
    residence = CharField(max_length=500)
    birthday = DateField()
    id_series = CharField(max_length=2)
    id_number = PositiveIntegerField()
    id_emitted_by = CharField(max_length=100)
    id_emitted_at = DateField()
    face = ImageField()
    back = ImageField()
    generated_doc = FileField()

    @cached_property
    def name(self):
        return str(self.first_name) + " " + str(self.last_name)

    def save(self, *args, **kwargs):
        document: Document = Open(
            os.path.join(settings.BASE_DIR, "templates", "template-procura.docx")
        )
        for paragraph in document.paragraphs:
            for attr_name in re.findall(variables_pattern, paragraph.text):
                if value := getattr(self, attr_name, None):
                    paragraph.text = paragraph.text.replace(
                        "{{" + attr_name + "}}", str(value)
                    )
                else:
                    print(f"Attribute {attr_name} not found!")

        new_document_name = f"{self.name}.docx"
        document.save(os.path.join(settings.MEDIA_ROOT, new_document_name))
        self.generated_doc = new_document_name
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "clients"


class IdUpload(Model):
    face = ImageField()
    back = ImageField()

    class Meta:
        managed = False
