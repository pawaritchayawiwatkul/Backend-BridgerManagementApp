# Generated by Django 5.0.4 on 2024-06-02 03:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0007_alter_courseregistration_course_alter_lesson_course_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='student',
        ),
    ]
