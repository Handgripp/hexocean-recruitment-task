# Generated by Django 4.2.5 on 2023-09-20 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_user_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='email',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='users',
            name='plan',
            field=models.CharField(max_length=10),
        ),
    ]
