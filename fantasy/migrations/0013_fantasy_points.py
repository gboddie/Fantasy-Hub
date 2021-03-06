# Generated by Django 2.1.1 on 2018-09-27 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0012_league_users_draft_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fantasy_Points',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=4)),
                ('passing', models.IntegerField(default=0)),
                ('rushing', models.IntegerField(default=0)),
                ('receiving', models.IntegerField(default=0)),
                ('catches', models.IntegerField(default=0)),
                ('kick_return', models.IntegerField(default=0)),
                ('punt_return', models.IntegerField(default=0)),
                ('fumbles', models.IntegerField(default=0)),
                ('Interceptions', models.IntegerField(default=0)),
                ('sacks', models.IntegerField(default=0)),
                ('safetys', models.IntegerField(default=0)),
                ('TDs', models.IntegerField(default=0)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasy.Players')),
            ],
        ),
    ]
