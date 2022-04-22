import datetime
import os.path
import re
from typing import final, AnyStr, Final

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models import (
    Model,
    SlugField,
    CharField,
    PositiveIntegerField,
    DateField,
    ImageField,
    FileField,
    ForeignKey,
    CASCADE,
    SET_NULL,
    DecimalField,
)
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from docx import Document as Open
from docx.document import Document
from model_utils import Choices
from model_utils.fields import MonitorField
from model_utils.models import TimeStampedModel, StatusModel

from common.constants import NUMBERS, MONTHS, YEARS
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


VARIABLES_PATTERN = re.compile("{{(.*?)}}")


@final
class Template(TimeStampedModel, BaseModel):
    name = CharField(max_length=500)
    file = FileField(
        upload_to="templates/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["docx"],
                message="Incarcă numai fișiere Microsoft Word (.docx)",
            )
        ],
    )

    def __str__(self):
        return f"{self.name} ({str(self.file.name).rsplit('/')[1]})"

    class Meta:
        db_table = "templates"


@final
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
    cost = DecimalField(
        verbose_name="Cost asistență notarială", max_digits=10, decimal_places=2
    )
    tax = DecimalField(verbose_name="Taxa de stat", max_digits=10, decimal_places=2)
    registration_number = CharField(max_length=100)
    face = ImageField()
    back = ImageField()
    template = ForeignKey(Template, on_delete=SET_NULL, null=True)
    generated_doc = FileField()

    @cached_property
    def name(self):
        return str(self.first_name) + " " + str(self.last_name)

    def save(self, *args, **kwargs):
        document: Document = Open(self.template.file.file)
        for paragraph in document.paragraphs:
            for attr_name in re.findall(VARIABLES_PATTERN, paragraph.text):
                if value := getattr(self, attr_name, None):
                    attribute = "{{" + attr_name + "}}"
                    paragraph.text = paragraph.text.replace(attribute, str(value))
                else:
                    print(f"Attribute {attr_name} not found!")

        now = datetime.datetime.now().strftime("%Y_%m_%d")
        new_document_name = f"{self.name}--{self.template_name}--{now}.docx"
        document.save(os.path.join(settings.MEDIA_ROOT, new_document_name))
        self.generated_doc = new_document_name
        return super().save(*args, **kwargs)

    @cached_property
    def year(self):
        return YEARS[datetime.datetime.now().year]

    @cached_property
    def month(self):
        return MONTHS[datetime.datetime.now().month]

    @cached_property
    def day(self):
        return NUMBERS[datetime.datetime.now().day]

    @cached_property
    def template_name(self):
        return self.template.name.replace(" ", "_").replace("/", "_").replace("\\", "_")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "clients"


class IdUpload(Model):
    face = ImageField()
    back = ImageField()
    template = ForeignKey(Template, on_delete=CASCADE)
    cost = DecimalField(
        verbose_name="Cost asistență notarială", max_digits=10, decimal_places=2
    )
    tax = DecimalField(verbose_name="Taxa de stat", max_digits=10, decimal_places=2)
    registration_number = CharField(max_length=100)

    class Meta:
        managed = False
