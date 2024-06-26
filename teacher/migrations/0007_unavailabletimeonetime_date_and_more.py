# Generated by Django 4.2.13 on 2024-06-13 13:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0006_rename_datetime_unavailabletimeonetime_start_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='unavailabletimeonetime',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='unavailabletimeonetime',
            name='start',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='unavailabletimeonetime',
            name='stop',
            field=models.TimeField(),
        ),
    ]
