# Generated by Django 4.0.4 on 2022-04-22 08:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_template_client_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Cost asistență notarială'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='registration_number',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Taxa de stat'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='template',
            name='file',
            field=models.FileField(upload_to='templates/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'], message='Incarcă numai fișiere Microsoft Word (.docx)')]),
        ),
    ]
