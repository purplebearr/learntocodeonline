# Generated by Django 4.2.7 on 2024-05-26 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='isContentPage',
            field=models.BooleanField(default=False),
        ),
    ]
