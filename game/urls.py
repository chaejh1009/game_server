from django.urls import path
from game import views
from game import views as game_views
from game import ad_events

app_name = "game"

urlpatterns = [
    path("play/", views.play, name="play"),
    path("api/player/", views.player_view, name="player"),
    path("api/delivery/", views.delivery_view, name="delivery"),
    path("api/history/", game_views.history, name="game-history"),
    path("api/auth/csrf/", views.csrf_view, name="csrf"),
    path("api/auth/login/", views.api_login, name="api-login"),
    path("ads-preview/", views.ad_preview, name="ad-preview"),
    path("api/ads/decision/", views.ad_decision, name="ad-decision"),
    path("api/ads/events/", ad_events.ad_event, name="ad-events"),
    path("api/ads/context/", views.ad_context, name="ad-context"),
]