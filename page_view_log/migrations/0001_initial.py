# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PageViewLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('session_key', models.CharField(max_length=32)),
                ('ip_address', models.CharField(max_length=15)),
                ('gen_time', models.BigIntegerField(null=True, blank=True)),
                ('status_code', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url_hash', models.CharField(max_length=32, db_index=True)),
                ('url_string', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='UserAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_agent_hash', models.CharField(max_length=32, db_index=True)),
                ('user_agent_string', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ViewName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('view_name_hash', models.CharField(max_length=32, db_index=True)),
                ('view_name_string', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='pageviewlog',
            name='url',
            field=models.ForeignKey(to='page_view_log.Url'),
        ),
        migrations.AddField(
            model_name='pageviewlog',
            name='user',
            field=models.ForeignKey(related_name='page_view_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pageviewlog',
            name='user_agent_hash',
            field=models.ForeignKey(to='page_view_log.UserAgent'),
        ),
        migrations.AddField(
            model_name='pageviewlog',
            name='view_name',
            field=models.ForeignKey(to='page_view_log.ViewName'),
        ),
    ]
