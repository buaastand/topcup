# Generated by Django 2.2.1 on 2019-06-30 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expert',
            old_name='actiavted',
            new_name='activated',
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='type',
            field=models.IntegerField(choices=[(1, 'student'), (2, 'admin'), (3, 'expert')], verbose_name='用户类型'),
        ),
    ]
