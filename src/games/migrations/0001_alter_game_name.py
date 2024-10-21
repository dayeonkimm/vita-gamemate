# Generated by Django 5.1.2 on 2024-10-19 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "add_games"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(
                choices=[
                    ("리그 오브 레전드", "리그 오브 레전드"),
                    ("오버워치", "오버워치"),
                    ("전략적 팀 전투", "전략적 팀 전투"),
                    ("배틀그라운드", "배틀그라운드"),
                ],
                max_length=255,
            ),
        ),
    ]
