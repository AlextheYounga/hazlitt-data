# Generated by Django 3.2 on 2021-07-18 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0006_auto_20210711_2114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stocknews',
            old_name='companyName',
            new_name='name',
        ),
    ]