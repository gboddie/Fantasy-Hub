# Generated by Django 2.1.1 on 2018-10-03 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0022_auto_20181003_1633'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fantasy_points',
            old_name='total_points',
            new_name='total_point',
        ),
        migrations.RenameField(
            model_name='stats',
            old_name='passing_yards',
            new_name='passing_yard',
        ),
    ]