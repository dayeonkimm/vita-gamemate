# Generated by Django 5.1.2 on 2024-10-29 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("chats", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="message",
            old_name="text",
            new_name="message",
        ),
    ]
