from django.db import models

from users.models import User


class MateGameInfoManager(models.Manager):
    def create(self, user_id, **kwargs):
        mategameinfo = self.model(
            user_id=user_id,
            **kwargs,
        )

        mategameinfo.full_clean()
        mategameinfo.save()

        user = User.objects.get_user_by_id(user_id)
        user.is_mate = True
        user.save()

        return mategameinfo

    def get_mate_game_info_from_id_and_game_id(self, mate_id: int, game_id: int):
        try:
            return self.model.objects.get(user_id=mate_id, game_id=game_id)
        except self.model.DoesNotExist:
            return None
