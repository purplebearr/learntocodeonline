# Generated by Django 5.0.6 on 2024-08-24 18:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_userproject'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassroomAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted_time', models.DateTimeField(auto_now_add=True)),
                ('classroom_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.classroomgroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
