# Generated by Django 5.0.6 on 2024-09-12 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0043_classroomgroup_banner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.CharField(default='Default Description', max_length=400),
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=200, null=True, unique=True),
        ),
    ]
