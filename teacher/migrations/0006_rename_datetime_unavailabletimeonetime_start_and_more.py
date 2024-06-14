# Generated by Django 4.2.13 on 2024-06-13 13:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0005_teacher_course'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unavailabletimeonetime',
            old_name='datetime',
            new_name='start',
        ),
        migrations.RenameField(
            model_name='unavailabletimeregular',
            old_name='time',
            new_name='start',
        ),
        migrations.RemoveField(
            model_name='unavailabletimeonetime',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='unavailabletimeregular',
            name='duration',
        ),
        migrations.AddField(
            model_name='unavailabletimeonetime',
            name='stop',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unavailabletimeregular',
            name='stop',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
