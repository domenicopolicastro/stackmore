# Generated by Django 4.2.13 on 2024-07-06 09:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_thread_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscribed_threads', to=settings.AUTH_USER_MODEL),
        ),
    ]
