# Generated by Django 4.2.13 on 2024-06-16 10:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0002_remove_course_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='registered_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
