# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookworm_app', '0002_auto_20150328_1812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='media_id',
        ),
        migrations.DeleteModel(
            name='Book',
        ),
        migrations.RemoveField(
            model_name='borrowrequest',
            name='from_id',
        ),
        migrations.RemoveField(
            model_name='borrowrequest',
            name='media_id',
        ),
        migrations.RemoveField(
            model_name='borrowrequest',
            name='to_id',
        ),
        migrations.DeleteModel(
            name='BorrowRequest',
        ),
        migrations.RemoveField(
            model_name='friendlist',
            name='friend_id',
        ),
        migrations.RemoveField(
            model_name='friendlist',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='FriendList',
        ),
        migrations.RemoveField(
            model_name='game',
            name='media_id',
        ),
        migrations.DeleteModel(
            name='Game',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='media_id',
        ),
        migrations.DeleteModel(
            name='Movie',
        ),
        migrations.RemoveField(
            model_name='userownsmedia',
            name='media_id',
        ),
        migrations.RemoveField(
            model_name='userownsmedia',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='UserOwnsMedia',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.RemoveField(
            model_name='userreviewsmedia',
            name='media_id',
        ),
        migrations.DeleteModel(
            name='Media',
        ),
        migrations.RemoveField(
            model_name='userreviewsmedia',
            name='review_id',
        ),
        migrations.DeleteModel(
            name='Review',
        ),
        migrations.RemoveField(
            model_name='userreviewsmedia',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='UserReviewsMedia',
        ),
    ]
