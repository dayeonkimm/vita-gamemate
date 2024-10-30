from django.urls import path

from game_requests.views.game_request_view import (
    GameRequestAcceptAPIView,
    GameRequestCancelAPIView,
    GameRequestCreateAPIView,
    GameRequestOrderedAPIView,
    GameRequestReceivedAPIView,
)

urlpatterns = [
    path("<int:user_id>/", GameRequestCreateAPIView.as_view(), name="game-request-create"),
    path("ordered/", GameRequestOrderedAPIView.as_view(), name="ordered-game-request"),
    path("received/", GameRequestReceivedAPIView.as_view(), name="received-game-request"),
    path("accept/<int:game_request_id>/", GameRequestAcceptAPIView.as_view(), name="accept-game-request"),
    path("cancel/<int:game_request_id>/", GameRequestCancelAPIView.as_view(), name="cancel-game-request"),
]
