# Generated by Django 5.0.6 on 2024-09-09 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0042_alter_lessonpage_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroomgroup',
            name='banner',
            field=models.ImageField(default='avatar.svg', upload_to=''),
        ),
    ]
