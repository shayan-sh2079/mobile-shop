# Generated by Django 5.0.2 on 2024-03-17 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='credit',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
