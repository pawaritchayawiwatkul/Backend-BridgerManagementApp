# Generated by Django 5.0.4 on 2024-06-06 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='birth_date',
        ),
    ]
