from django.db import models


class GameRequestManager(models.Manager):
    def create(self, user_id, mate_id, **kwargs):
        game_request = self.model(
            user_id=user_id,
            mate_id=mate_id,
            **kwargs,
        )

        game_request.full_clean()
        game_request.save()

        return game_request

    def accept(self, game_request):
        game_request.status = True
        game_request.save()

        return game_request

    def reject(self, game_request):
        game_request.status = False
        game_request.save()

        return game_request
