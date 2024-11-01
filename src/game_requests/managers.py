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

    def get_game_request_from_id(self, id):
        try:
            return self.get(id=id)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist

    def get_game_request_game_review_count(self, mate_id, game_id, review_status=True):
        try:
            return self.filter(mate_id=mate_id, game_id=game_id, review_status=review_status).count()
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist

    def get_game_request_total_count(self, mate_id):
        try:
            return self.filter(mate_id=mate_id).count()
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist

    def get_game_request_count(self, mate_id, game_id):
        try:
            return self.filter(mate_id=mate_id, game_id=game_id).count()
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist

    def accept(self, game_request):
        game_request.status = True
        game_request.save()

        return game_request

    def reject(self, game_request):
        game_request.delete()

        return None

    def cancel(self, game_request):
        game_request.delete()

        return None
