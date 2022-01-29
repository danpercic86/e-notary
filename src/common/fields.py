from django.db import models


class BigIntegerRangeField(models.BigIntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None,
                 **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.BigIntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(BigIntegerRangeField, self).formfield(**defaults)
