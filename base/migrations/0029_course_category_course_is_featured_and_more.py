# Generated by Django 5.0.6 on 2024-06-30 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_course_is_private_lesson_is_private_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.TextField(default='default'),
        ),
        migrations.AddField(
            model_name='course',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='course',
            name='is_trending',
            field=models.BooleanField(default=False),
        ),
    ]
