# Generated by Django 4.2.7 on 2024-05-27 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_lessonpage_canvaembedurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='svg_file',
            field=models.ImageField(default='static/images/avatar.svg', upload_to=''),
        ),
    ]
