# Generated by Django 4.0.1 on 2022-01-29 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_idupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='back',
            field=models.ImageField(default="", upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='face',
            field=models.ImageField(default="", upload_to=''),
            preserve_default=False,
        ),
    ]