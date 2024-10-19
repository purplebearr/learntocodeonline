# Generated by Django 5.0.6 on 2024-06-27 04:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_remove_quicklink_url_quicklink_external_url_and_more'),
        ('wagtailcore', '0093_uploadedfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quicklink',
            name='external_url',
        ),
        migrations.AlterField(
            model_name='quicklink',
            name='link_page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.page'),
        ),
    ]
