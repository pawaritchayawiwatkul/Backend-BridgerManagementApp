# Generated by Django 4.2.13 on 2024-06-13 02:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_alter_teacher_school'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='course',
        ),
    ]
