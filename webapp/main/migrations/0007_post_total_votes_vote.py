# Generated by Django 4.2.13 on 2024-07-06 13:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0006_post_thread'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='total_votes',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='main.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'post')},
            },
        ),
    ]
