# Generated by Django 2.1.1 on 2018-09-27 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0018_auto_20180927_1452'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='league_users',
            unique_together=set(),
        ),
    ]
