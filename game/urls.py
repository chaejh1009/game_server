from django.urls import path
from game import views
from game import views as game_views

app_name = "game"

urlpatterns = [
    path("play/", views.play, name="play"),
    path("api/player/", views.player_view, name="player"),
    path("api/delivery/",views.delivery_view,name ="delivery"),
    path("api/history/", game_views.history, name="game-history"),
]