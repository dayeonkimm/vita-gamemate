# Generated by Django 5.1.2 on 2024-10-31 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_remove_user_last_activity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="nickname",
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
