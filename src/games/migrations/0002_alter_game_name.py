# Generated by Django 5.1.2 on 2024-10-18 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(
                choices=[("lol", "리그 오브 레전드"), ("overwatch", "오버워치"), ("tft", "전략적 팀 전투"), ("bg", "배틀그라운드")],
                max_length=255,
            ),
        ),
    ]
