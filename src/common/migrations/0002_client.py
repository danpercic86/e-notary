# Generated by Django 4.0.1 on 2022-01-29 13:40

import common.fileds
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=300)),
                ('last_name', models.CharField(max_length=300)),
                ('cnp', common.fileds.BigIntegerRangeField()),
                ('residence', models.CharField(max_length=500)),
                ('birthday', models.DateField()),
                ('id_series', models.CharField(max_length=2)),
                ('id_number', models.PositiveIntegerField()),
                ('id_emitted_by', models.CharField(max_length=100)),
                ('id_emitted_at', models.DateField()),
            ],
            options={
                'db_table': 'clients',
            },
        ),
    ]