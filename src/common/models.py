from typing import final, AnyStr, Final

from django.db.models import Model, SlugField, CharField, PositiveIntegerField, \
    DateField, ImageField
from django.utils.translation import gettext as _
from model_utils import Choices
from model_utils.fields import MonitorField
from model_utils.models import TimeStampedModel, StatusModel

from common.fields import BigIntegerRangeField


class SlugableModel(Model):
    slug = SlugField(unique=True, db_index=True)

    class Meta:
        abstract = True


class BaseModel(Model):
    class Meta:
        abstract = True

    def get_change_url(self) -> AnyStr:
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

        return format_html(f"<a href='{self.get_change_url()}'>{self}</a>")


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


class Client(TimeStampedModel, BaseModel):
    first_name = CharField(max_length=300)
    last_name = CharField(max_length=300)
    cnp = BigIntegerRangeField(min_value=1000000000000, max_value=6999999999999)
    residence = CharField(max_length=500)
    id_number = PositiveIntegerField()
    id_series = CharField(max_length=2)
    id_emitted_by = CharField(max_length=100)
    id_emitted_at = DateField()
    birthday = DateField()
    front = ImageField()
    back = ImageField()

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)

    class Meta:
        db_table = "clients"

class IdUpload(Model):
    front = ImageField()
    back = ImageField()

    class Meta:
        managed = False
