from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0002_game_views_alter_game_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(choices=[("lol", "lol"), ("overwatch", "overwatch"), ("tft", "tft"), ("bg", "bg")], max_length=255),
        ),
    ]
