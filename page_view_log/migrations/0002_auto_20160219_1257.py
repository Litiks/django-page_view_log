# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page_view_log', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pageviewlog',
            old_name='user_agent_hash',
            new_name='user_agent',
        ),
    ]
