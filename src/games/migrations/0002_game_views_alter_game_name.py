# Generated by Django 5.1.2 on 2024-10-21 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0001_alter_game_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="views",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(
                choices=[
                    ("리그오브레전드", "리그오브레전드"),
                    ("오버워치", "오버워치"),
                    ("전략적팀전투", "전략적팀전투"),
                    ("배틀그라운드", "배틀그라운드"),
                ],
                max_length=255,
            ),
        ),
    ]
